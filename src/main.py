import argparse
import asyncio
import json
import os
import threading
import traceback
import logging
from pathlib import Path
from typing import Any, Dict, Iterable, AsyncIterable, AsyncGenerator, Optional
import sys
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(project_root / "src") not in sys.path:
    sys.path.insert(0, str(project_root / "src"))

# 设置工作空间环境变量
os.environ["COZE_WORKSPACE_PATH"] = str(project_root)

import cozeloop
import uvicorn
import time
from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from coze_coding_utils.runtime_ctx.context import new_context, Context
from coze_coding_utils.helper import graph_helper
from coze_coding_utils.log.node_log import LOG_FILE
from coze_coding_utils.log.write_log import setup_logging, request_context
from coze_coding_utils.log.config import LOG_LEVEL
from coze_coding_utils.error.classifier import ErrorClassifier, classify_error
from coze_coding_utils.helper.stream_runner import AgentStreamRunner, WorkflowStreamRunner,agent_stream_handler,workflow_stream_handler, RunOpt

setup_logging(
    log_file=LOG_FILE,
    max_bytes=100 * 1024 * 1024, # 100MB
    backup_count=5,
    log_level=LOG_LEVEL,
    use_json_format=True,
    console_output=True
)

logger = logging.getLogger(__name__)
from coze_coding_utils.helper.agent_helper import to_stream_input
from coze_coding_utils.openai.handler import OpenAIChatHandler
from coze_coding_utils.log.parser import LangGraphParser
from coze_coding_utils.log.err_trace import extract_core_stack
from coze_coding_utils.log.loop_trace import init_run_config, init_agent_config


# 超时配置常量
TIMEOUT_SECONDS = 900  # 15分钟

# 鉴权配置
AUTH_TOKEN_EXPIRE_HOURS = 24  # token有效期24小时
AUTH_USERNAME = "YNTB"
AUTH_PASSWORD = "yntb123"

# 存储有效的token (简单实现,生产环境应该使用数据库或Redis)
active_tokens: Dict[str, datetime] = {}

# 导入文件监控和WebSocket管理模块
from utils.file_watcher import start_file_watcher, stop_file_watcher
from utils.websocket_manager import manager, notify_data_updated, MessageType

# 生成简单的token (生产环境应该使用JWT)
def generate_token() -> str:
    """生成简单的token"""
    import uuid
    return str(uuid.uuid4())

# 验证token
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> str:
    """验证token的有效性"""
    token = credentials.credentials
    
    if token not in active_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的token,请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查token是否过期
    expire_time = active_tokens[token]
    if datetime.now() > expire_time:
        del active_tokens[token]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token已过期,请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token

# 可选的token验证 (某些路由不需要登录)
def verify_token_optional(request: Request) -> Optional[str]:
    """可选的token验证,如果没有token则返回None"""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.split(" ")[1]
        if token not in active_tokens:
            return None
        
        expire_time = active_tokens[token]
        if datetime.now() > expire_time:
            del active_tokens[token]
            return None
        
        return token
    except:
        return None

class GraphService:
    def __init__(self):
        # 用于跟踪正在运行的任务（使用asyncio.Task）
        self.running_tasks: Dict[str, asyncio.Task] = {}
        # 错误分类器
        self.error_classifier = ErrorClassifier()
        # stream runner
        self._agent_stream_runner = AgentStreamRunner()
        self._workflow_stream_runner = WorkflowStreamRunner()
        self._graph = None
        self._graph_lock = threading.Lock()

    def _get_graph(self, ctx=None):
        if graph_helper.is_agent_proj():
            return graph_helper.get_agent_instance("agents.agent", ctx)

        if self._graph is not None:
            return self._graph
        with self._graph_lock:
            if self._graph is not None:
                return self._graph
            self._graph = graph_helper.get_graph_instance("graphs.graph")
            return self._graph

    @staticmethod
    def _sse_event(data: Any, event_id: Any = None) -> str:
        id_line = f"id: {event_id}\n" if event_id else ""
        return f"{id_line}event: message\ndata: {json.dumps(data, ensure_ascii=False, default=str)}\n\n"

    def _get_stream_runner(self):
        if graph_helper.is_agent_proj():
            return self._agent_stream_runner
        else:
            return self._workflow_stream_runner

    # 流式运行（原始迭代器）：本地调用使用
    def stream(self, payload: Dict[str, Any], run_config: RunnableConfig, ctx=Context) -> Iterable[Any]:
        graph = self._get_graph(ctx)
        stream_runner = self._get_stream_runner()
        for chunk in stream_runner.stream(payload, graph, run_config, ctx):
            yield chunk

    # 同步运行：本地/HTTP 通用
    async def run(self, payload: Dict[str, Any], ctx=None) -> Dict[str, Any]:
        if ctx is None:
            ctx = new_context("run")

        run_id = ctx.run_id
        logger.info(f"Starting run with run_id: {run_id}")

        try:
            graph = self._get_graph(ctx)
            # custom tracer
            run_config = init_run_config(graph, ctx)
            run_config["configurable"] = {"thread_id": ctx.run_id}

            # 直接调用，LangGraph会在当前任务上下文中执行
            # 如果当前任务被取消，LangGraph的执行也会被取消
            return await graph.ainvoke(payload, config=run_config, context=ctx)

        except asyncio.CancelledError:
            logger.info(f"Run {run_id} was cancelled")
            return {"status": "cancelled", "run_id": run_id, "message": "Execution was cancelled"}
        except Exception as e:
            # 使用错误分类器分类错误
            err = self.error_classifier.classify(e, {"node_name": "run", "run_id": run_id})
            # 记录详细的错误信息和堆栈跟踪
            logger.error(
                f"Error in GraphService.run: [{err.code}] {err.message}\n"
                f"Category: {err.category.name}\n"
                f"Traceback:\n{extract_core_stack()}"
            )
            # 保留原始异常堆栈，便于上层返回真正的报错位置
            raise
        finally:
            # 清理任务记录
            self.running_tasks.pop(run_id, None)

    # 流式运行（SSE 格式化）：HTTP 路由使用
    async def stream_sse(self, payload: Dict[str, Any], ctx=None, run_opt: Optional[RunOpt] = None) -> AsyncGenerator[str, None]:
        if ctx is None:
            ctx = new_context(method="stream_sse")
        if run_opt is None:
            run_opt = RunOpt()

        run_id = ctx.run_id
        logger.info(f"Starting stream with run_id: {run_id}")
        graph = self._get_graph(ctx)
        if graph_helper.is_agent_proj():
            run_config = init_agent_config(graph, ctx)
        else:
            run_config = init_run_config(graph, ctx)  # vibeflow

        is_workflow = not graph_helper.is_agent_proj()

        try:
            async for chunk in self.astream(payload, graph, run_config=run_config, ctx=ctx, run_opt=run_opt):
                if is_workflow and isinstance(chunk, tuple):
                    event_id, data = chunk
                    yield self._sse_event(data, event_id)
                else:
                    yield self._sse_event(chunk)
        finally:
            # 清理任务记录
            self.running_tasks.pop(run_id, None)
            cozeloop.flush()

    # 取消执行 - 使用asyncio的标准方式
    def cancel_run(self, run_id: str, ctx: Optional[Context] = None) -> Dict[str, Any]:
        """
        取消指定run_id的执行

        使用asyncio.Task.cancel()来取消任务,这是标准的Python异步取消机制。
        LangGraph会在节点之间检查CancelledError,实现优雅的取消。
        """
        logger.info(f"Attempting to cancel run_id: {run_id}")

        # 查找对应的任务
        if run_id in self.running_tasks:
            task = self.running_tasks[run_id]
            if not task.done():
                # 使用asyncio的标准取消机制
                # 这会在下一个await点抛出CancelledError
                task.cancel()
                logger.info(f"Cancellation requested for run_id: {run_id}")
                return {
                    "status": "success",
                    "run_id": run_id,
                    "message": "Cancellation signal sent, task will be cancelled at next await point"
                }
            else:
                logger.info(f"Task already completed for run_id: {run_id}")
                return {
                    "status": "already_completed",
                    "run_id": run_id,
                    "message": "Task has already completed"
                }
        else:
            logger.warning(f"No active task found for run_id: {run_id}")
            return {
                "status": "not_found",
                "run_id": run_id,
                "message": "No active task found with this run_id. Task may have already completed or run_id is invalid."
            }

    # 运行指定节点：本地/HTTP 通用
    async def run_node(self, node_id: str, payload: Dict[str, Any], ctx=None) -> Any:
        if ctx is None or Context.run_id == "":
            ctx = new_context(method="node_run")

        _graph = self._get_graph()
        node_func, input_cls, output_cls = graph_helper.get_graph_node_func_with_inout(_graph.get_graph(), node_id)
        if node_func is None or input_cls is None:
            raise KeyError(f"node_id '{node_id}' not found")

        parser = LangGraphParser(_graph)
        metadata = parser.get_node_metadata(node_id) or {}

        _g = StateGraph(input_cls, input_schema=input_cls, output_schema=output_cls)
        _g.add_node("sn", node_func, metadata=metadata)
        _g.set_entry_point("sn")
        _g.add_edge("sn", END)
        _graph = _g.compile()

        run_config = init_run_config(_graph, ctx)
        return await _graph.ainvoke(payload, config=run_config)

    def graph_inout_schema(self) -> Any:
        if graph_helper.is_agent_proj():
            return {"input_schema": {}, "output_schema": {}}
        builder = getattr(self._get_graph(), 'builder', None)
        if builder is not None:
            input_cls = getattr(builder, 'input_schema', None) or self.graph.get_input_schema()
            output_cls = getattr(builder, 'output_schema', None) or self.graph.get_output_schema()
        else:
            logger.warning(f"No builder input schema found for graph_inout_schema, using graph input schema instead")
            input_cls = self.graph.get_input_schema()
            output_cls = self.graph.get_output_schema()

        return {
            "input_schema": input_cls.model_json_schema(),
            "output_schema": output_cls.model_json_schema(),
            "code":0,
            "msg":""
        }

    async def astream(self, payload: Dict[str, Any], graph: CompiledStateGraph, run_config: RunnableConfig, ctx=Context, run_opt: Optional[RunOpt] = None) -> AsyncIterable[Any]:
        stream_runner = self._get_stream_runner()
        async for chunk in stream_runner.astream(payload, graph, run_config, ctx, run_opt):
            yield chunk


service = GraphService()
app = FastAPI(title="航空公司产品智能体", description="航空公司产品查询系统", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
workspace_path = os.getenv("COZE_WORKSPACE_PATH", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
static_dir = Path(workspace_path) / "static"
if not static_dir.exists():
    static_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# 主页路由 - 需要登录
@app.get("/")
async def root(request: Request):
    """主页,直接返回主页HTML,由前端JavaScript检查登录状态"""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    else:
        return {"message": "Airline Product System", "status": "running"}

# 登录页面路由 (无需鉴权)
@app.get("/login")
async def login_page():
    """登录页面"""
    login_file = static_dir / "login.html"
    if login_file.exists():
        return FileResponse(str(login_file))
    return {"message": "Login page not found"}

# 登录API
@app.post("/api/login")
async def login(request: Request):
    """用户登录接口"""
    try:
        body = await request.json()
        username = body.get("username", "").strip()
        password = body.get("password", "")
        
        # 验证账号密码
        if username == AUTH_USERNAME and password == AUTH_PASSWORD:
            # 生成token
            token = generate_token()
            expire_time = datetime.now() + timedelta(hours=AUTH_TOKEN_EXPIRE_HOURS)
            active_tokens[token] = expire_time
            
            return JSONResponse({
                "success": True,
                "token": token,
                "message": "登录成功"
            })
        else:
            return JSONResponse({
                "success": False,
                "message": "账号或密码错误"
            }, status_code=401)
    except Exception as e:
        logger.error(f"登录错误: {str(e)}")
        return JSONResponse({
            "success": False,
            "message": "登录失败,请稍后重试"
        }, status_code=500)

# 登出API
@app.post("/api/logout")
async def logout(request: Request):
    """用户登出接口"""
    try:
        token = verify_token_optional(request)
        if token and token in active_tokens:
            del active_tokens[token]
        
        return JSONResponse({
            "success": True,
            "message": "登出成功"
        })
    except Exception as e:
        logger.error(f"登出错误: {str(e)}")
        return JSONResponse({
            "success": False,
            "message": "登出失败"
        }, status_code=500)

# 验证token状态API
@app.get("/api/auth/status")
async def auth_status(request: Request):
    """检查登录状态"""
    token = verify_token_optional(request)
    if token:
        expire_time = active_tokens[token]
        remaining_time = int((expire_time - datetime.now()).total_seconds())
        return JSONResponse({
            "success": True,
            "logged_in": True,
            "remaining_seconds": remaining_time
        })
    else:
        return JSONResponse({
            "success": True,
            "logged_in": False
        })

# OpenAI 兼容接口处理器
openai_handler = OpenAIChatHandler(service)


@app.post("/run")
async def http_run(request: Request) -> Dict[str, Any]:
    global result
    raw_body = await request.body()
    try:
        body_text = raw_body.decode("utf-8")
    except Exception as e:
        body_text = str(raw_body)
        raise HTTPException(status_code=400,
                            detail=f"Invalid JSON format: {body_text}, traceback: {traceback.format_exc()}, error: {e}")

    ctx = new_context(method="run", headers=request.headers)
    run_id = ctx.run_id
    request_context.set(ctx)

    logger.info(
        f"Received request for /run: "
        f"run_id={run_id}, "
        f"query={dict(request.query_params)}, "
        f"body={body_text}"
    )

    try:
        payload = await request.json()

        # 创建任务并记录 - 这是关键，让我们可以通过run_id取消任务
        task = asyncio.create_task(service.run(payload, ctx))
        service.running_tasks[run_id] = task

        try:
            result = await asyncio.wait_for(task, timeout=float(TIMEOUT_SECONDS))
        except asyncio.TimeoutError:
            logger.error(f"Run execution timeout after {TIMEOUT_SECONDS}s for run_id: {run_id}")
            task.cancel()
            try:
                result = await task
            except asyncio.CancelledError:
                return {
                    "status": "timeout",
                    "run_id": run_id,
                    "message": f"Execution timeout: exceeded {TIMEOUT_SECONDS} seconds"
                }

        if not result:
            result = {}
        if isinstance(result, dict):
            result["run_id"] = run_id
        return result

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in http_run: {e}, traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON format, {extract_core_stack()}")

    except asyncio.CancelledError:
        logger.info(f"Request cancelled for run_id: {run_id}")
        result = {"status": "cancelled", "run_id": run_id, "message": "Execution was cancelled"}
        return result

    except Exception as e:
        # 使用错误分类器获取错误信息
        error_response = service.error_classifier.get_error_response(e, {"node_name": "http_run", "run_id": run_id})
        logger.error(
            f"Unexpected error in http_run: [{error_response['error_code']}] {error_response['error_message']}, "
            f"traceback: {traceback.format_exc()}", exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": error_response["error_code"],
                "error_message": error_response["error_message"],
                "stack_trace": extract_core_stack(),
            }
        )
    finally:
        cozeloop.flush()


HEADER_X_WORKFLOW_STREAM_MODE = "x-workflow-stream-mode"


def _register_task(run_id: str, task: asyncio.Task):
    service.running_tasks[run_id] = task


@app.post("/stream_run")
async def http_stream_run(request: Request):
    ctx = new_context(method="stream_run", headers=request.headers)
    workflow_stream_mode = request.headers.get(HEADER_X_WORKFLOW_STREAM_MODE, "").lower()
    workflow_debug = workflow_stream_mode == "debug"
    request_context.set(ctx)
    raw_body = await request.body()
    try:
        body_text = raw_body.decode("utf-8")
    except Exception as e:
        body_text = str(raw_body)
        raise HTTPException(status_code=400,
                            detail=f"Invalid JSON format: {body_text}, {extract_core_stack()}, error: {e}")
    run_id = ctx.run_id
    is_agent = graph_helper.is_agent_proj()
    logger.info(
        f"Received request for /stream_run: "
        f"run_id={run_id}, "
        f"is_agent_project={is_agent}, "
        f"query={dict(request.query_params)}, "
        f"body={body_text}"
    )
    try:
        payload = await request.json()
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in http_stream_run: {e}, traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON format:{extract_core_stack()}")

    if is_agent:
        stream_generator = agent_stream_handler(
            payload=payload,
            ctx=ctx,
            run_id=run_id,
            stream_sse_func=service.stream_sse,
            sse_event_func=service._sse_event,
            error_classifier=service.error_classifier,
            register_task_func=_register_task,
        )
    else:
        stream_generator = workflow_stream_handler(
            payload=payload,
            ctx=ctx,
            run_id=run_id,
            stream_sse_func=service.stream_sse,
            sse_event_func=service._sse_event,
            error_classifier=service.error_classifier,
            register_task_func=_register_task,
            run_opt=RunOpt(workflow_debug=workflow_debug),
        )

    response = StreamingResponse(stream_generator, media_type="text/event-stream")
    return response

@app.post("/cancel/{run_id}")
async def http_cancel(run_id: str, request: Request):
    """
    取消指定run_id的执行

    使用asyncio.Task.cancel()实现取消,这是Python标准的异步任务取消机制。
    LangGraph会在节点之间的await点检查CancelledError,实现优雅取消。
    """
    ctx = new_context(method="cancel", headers=request.headers)
    request_context.set(ctx)
    logger.info(f"Received cancel request for run_id: {run_id}")
    result = service.cancel_run(run_id, ctx)
    return result


@app.post(path="/node_run/{node_id}")
async def http_node_run(node_id: str, request: Request):
    raw_body = await request.body()
    try:
        body_text = raw_body.decode("utf-8")
    except UnicodeDecodeError:
        body_text = str(raw_body)
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {body_text}")
    ctx = new_context(method="node_run", headers=request.headers)
    request_context.set(ctx)
    logger.info(
        f"Received request for /node_run/{node_id}: "
        f"query={dict(request.query_params)}, "
        f"body={body_text}",
    )

    try:
        payload = await request.json()
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in http_node_run: {e}, traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON format:{extract_core_stack()}")
    try:
        return await service.run_node(node_id, payload, ctx)
    except KeyError:
        raise HTTPException(status_code=404,
                            detail=f"node_id '{node_id}' not found or input miss required fields, traceback: {extract_core_stack()}")
    except Exception as e:
        # 使用错误分类器获取错误信息
        error_response = service.error_classifier.get_error_response(e, {"node_name": node_id})
        logger.error(
            f"Unexpected error in http_node_run: [{error_response['error_code']}] {error_response['error_message']}, "
            f"traceback: {traceback.format_exc()}", exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": error_response["error_code"],
                "error_message": error_response["error_message"],
                "stack_trace": extract_core_stack(),
            }
        )
    finally:
        cozeloop.flush()


@app.post("/v1/chat/completions")
async def openai_chat_completions(request: Request):
    """OpenAI Chat Completions API 兼容接口"""
    ctx = new_context(method="openai_chat", headers=request.headers)
    request_context.set(ctx)

    logger.info(f"Received request for /v1/chat/completions: run_id={ctx.run_id}")

    try:
        payload = await request.json()
        return await openai_handler.handle(payload, ctx)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in openai_chat_completions: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    finally:
        cozeloop.flush()


@app.get("/health")
async def health_check():
    try:
        # 这里可以添加更多的健康检查逻辑
        return {
            "status": "ok",
            "message": "Service is running",
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get(path="/graph_parameter")
async def http_graph_inout_parameter(request: Request):
    return service.graph_inout_schema()


# ============================================================================
# 前端 API 端点
# ============================================================================

@app.get("/api/airlines")
async def get_airlines_api(token: str = Depends(verify_token)):
    """获取所有航空公司列表 - 需要鉴权"""
    try:
        from agents.agent import get_agent_instance
        from utils.airline_names import AIRLINE_NAMES

        agent = get_agent_instance()

        # 从产品中提取航司代码和统计产品数量，保持产品表中航司的出现顺序
        airline_info = {}  # 航司代码 -> 航司名称
        airline_counts = {}  # 航司代码 -> 产品数量
        airline_order = []  # 航司代码出现的顺序

        for product in agent.products:
            if product.airline:
                if product.airline not in airline_info:
                    airline_info[product.airline] = AIRLINE_NAMES.get(product.airline, product.airline)
                    airline_counts[product.airline] = 0
                    airline_order.append(product.airline)
                airline_counts[product.airline] += 1

        # 按照产品表中航司的出现顺序创建列表
        airlines_list = [
            {"code": code, "name": airline_info[code], "count": airline_counts.get(code, 0)}
            for code in airline_order
        ]

        return {
            "success": True,
            "message": f"共有 {len(airlines_list)} 个航空公司",
            "data": {
                "count": len(airlines_list),
                "airlines": airlines_list
            }
        }
    except Exception as e:
        logger.error(f"获取航空公司列表失败: {e}")
        return {
            "success": False,
            "message": f"获取航空公司列表失败: {str(e)}",
            "data": {"count": 0, "airlines": []}
        }


@app.get("/api/airlines/{airline_code}")
async def get_airline_products_api(airline_code: str, token: str = Depends(verify_token)):
    """获取指定航空公司的所有产品 - 需要鉴权"""
    try:
        from agents.agent import get_agent_instance
        agent = get_agent_instance()

        products = agent.get_products_by_airline(airline_code.strip().upper())

        if not products:
            return {
                "success": True,
                "message": f"未找到航空公司 {airline_code} 的产品",
                "data": {
                    "airline_code": airline_code,
                    "count": 0,
                    "products": []
                }
            }

        products_data = [p.to_dict() for p in products]

        return {
            "success": True,
            "message": f"航空公司 {airline_code} 共有 {len(products)} 个产品",
            "data": {
                "airline_code": airline_code,
                "count": len(products),
                "products": products_data
            }
        }
    except Exception as e:
        logger.error(f"获取产品列表失败: {e}")
        return {
            "success": False,
            "message": f"获取产品列表失败: {str(e)}",
            "data": {"airline_code": airline_code, "count": 0, "products": []}
        }


@app.get("/api/search")
async def search_products_api(keyword: str, token: str = Depends(verify_token)):
    """搜索产品 - 需要鉴权"""
    try:
        from agents.agent import get_agent_instance
        agent = get_agent_instance()

        results = agent.search_products(keyword)

        if not results:
            return {
                "success": True,
                "message": "未找到匹配的产品",
                "data": {
                    "keyword": keyword,
                    "count": 0,
                    "products": []
                }
            }

        products_data = [p.to_dict() for p in results[:10]]  # 限制返回10条
        return {
            "success": True,
            "message": f"找到 {len(results)} 个匹配产品",
            "data": {
                "keyword": keyword,
                "count": len(results),
                "products": products_data
            }
        }
    except Exception as e:
        logger.error(f"搜索产品失败: {e}")
        return {
            "success": False,
            "message": f"搜索失败: {str(e)}",
            "data": {"keyword": keyword, "count": 0, "products": []}
        }


@app.post("/api/products/update-airlines")
async def update_product_airlines_api(token: str = Depends(verify_token)):
    """智能更新产品的航司字段 - 需要鉴权"""
    try:
        from agents.agent import get_agent_instance
        from utils.airline_names import AIRLINE_NAMES

        agent = get_agent_instance()

        # 航司简称映射
        AIRLINE_ALIASES = {
            '东航': 'MU', '上航': 'FM', '南航': 'CZ',
            '国航': 'CA', '海航': 'HU', '川航': '3U',
            '厦航': 'MF', '山航': 'SC', '深航': 'ZH',
            '昆航': 'KY', '长龙': 'GJ', '祥鹏': '8L',
            '首都': 'JD', '幸福': 'JR', '长安': '9H',
            '天津': 'GS', '北部湾': 'GX', '东海': 'DZ',
            '龙江': 'LT', '西部': 'PN', '西藏': 'TV',
            '成都': 'EU', '华夏': 'G5', '江西': 'RY',
            '青岛': 'QW', '河北': 'NS', '重庆': 'OQ',
            '福州': 'FU', '乌鲁木齐': 'UQ', '联合': 'KN',
            '奥凯': 'BK', '吉祥': 'HO', '大新华': 'CN',
            '红土': 'A6', '桂林': 'DR', '多彩贵州': 'GY'
        }

        def detect_airline_code(product):
            """智能识别航司代码"""
            product_name = product.product_name or ''
            route = product.route or ''
            office = product.office or ''

            # 方法1: 直接从airline字段获取
            if product.airline:
                return product.airline

            # 方法2: 从产品名称中查找航司二字码
            for code in AIRLINE_NAMES.keys():
                if code in product_name:
                    return code

            # 方法3: 从产品名称中查找航司全称
            for name, code in AIRLINE_NAMES.items():
                if name in product_name:
                    return code

            # 方法4: 从产品名称中查找航司简称
            for alias, code in AIRLINE_ALIASES.items():
                if alias in product_name:
                    return code

            # 方法5: 从路线中查找航司全称或简称
            if route:
                for name, code in AIRLINE_NAMES.items():
                    if name in route:
                        return code
                for alias, code in AIRLINE_ALIASES.items():
                    if alias in route:
                        return code

            # 方法6: 从Office字段中查找航司二字码
            if office:
                for code in AIRLINE_NAMES.keys():
                    if code in office:
                        return code

            # 未识别到航司
            return None

        # 统计
        total_products = len(agent.products)
        null_airline_products = [p for p in agent.products if not p.airline or str(p.airline).strip() == '']
        updated_count = 0

        # 按识别出的航司分组
        airline_product_map = {}

        for product in null_airline_products:
            detected_code = detect_airline_code(product)

            if detected_code:
                # 更新产品的airline字段
                product.airline = detected_code
                updated_count += 1

                if detected_code not in airline_product_map:
                    airline_product_map[detected_code] = []
                airline_product_map[detected_code].append(product)

        # 准备返回数据
        update_details = {}
        for code, products_list in airline_product_map.items():
            update_details[code] = {
                'airline_name': AIRLINE_NAMES.get(code, code),
                'count': len(products_list)
            }

        return {
            "success": True,
            "message": f"成功更新 {updated_count} 个产品的航司字段",
            "data": {
                "total_products": total_products,
                "null_airline_before": len(null_airline_products),
                "updated_count": updated_count,
                "update_details": update_details
            }
        }
    except Exception as e:
        logger.error(f"更新产品航司字段失败: {e}")
        return {
            "success": False,
            "message": f"更新失败: {str(e)}",
            "data": {}
        }

        return {
            "success": True,
            "message": f"找到 {len(results)} 个匹配产品（显示前10条）",
            "data": {
                "keyword": keyword,
                "count": len(results),
                "products": products_data
            }
        }
    except Exception as e:
        logger.error(f"搜索产品失败: {e}")
        return {
            "success": False,
            "message": f"搜索产品失败: {str(e)}",
            "data": {"keyword": keyword, "count": 0, "products": []}
        }


@app.get("/api/stats")
async def get_stats_api(token: str = Depends(verify_token)):
    """获取系统统计信息 - 需要鉴权"""
    try:
        from agents.agent import get_agent_instance
        agent = get_agent_instance()

        stats = agent.get_statistics()

        return {
            "success": True,
            "message": "智能体统计信息",
            "data": stats
        }
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        return {
            "success": False,
            "message": f"获取统计信息失败: {str(e)}",
            "data": {}
        }


@app.get("/api/ticket-types")
async def get_ticket_types_api(token: str = Depends(verify_token)):
    """获取所有票证类型及其数量 - 需要鉴权"""
    try:
        from agents.agent import get_agent_instance
        agent = get_agent_instance()

        ticket_types = {
            'GP': agent.get_products_by_ticket_type('GP'),
            'BSP': agent.get_products_by_ticket_type('BSP'),
            'B2B': agent.get_products_by_ticket_type('B2B'),
            'MULTI': agent.get_products_by_ticket_type('MULTI'),
            'ALL': agent.get_products_by_ticket_type('ALL')
        }

        ticket_type_stats = {
            ttype: len(products) for ttype, products in ticket_types.items()
        }

        return {
            "success": True,
            "message": "票证类型统计",
            "data": ticket_type_stats
        }
    except Exception as e:
        logger.error(f"获取票证类型统计失败: {e}")
        return {
            "success": False,
            "message": f"获取票证类型统计失败: {str(e)}",
            "data": {}
        }


@app.get("/api/products")
async def get_all_products_api(token: str = Depends(verify_token)):
    """获取所有产品数据 - 需要鉴权"""
    try:
        from agents.agent import get_agent_instance
        agent = get_agent_instance()

        products_data = [p.to_dict() for p in agent.products]

        return {
            "success": True,
            "message": f"共有 {len(products_data)} 个产品",
            "data": {
                "count": len(products_data),
                "products": products_data
            }
        }
    except Exception as e:
        logger.error(f"获取所有产品失败: {e}")
        return {
            "success": False,
            "message": f"获取所有产品失败: {str(e)}",
            "data": {"count": 0, "products": []}
        }


@app.post("/api/reload")
async def reload_products_api(token: str = Depends(verify_token)):
    """重新加载产品数据 - 需要鉴权"""
    try:
        from agents.agent import get_agent_instance, load_cleaned_data, create_airline_products

        logger.info("开始重新加载产品数据...")

        # 获取智能体实例
        agent = get_agent_instance()

        # 清空现有产品
        agent.products = []
        agent.airlines = set()
        agent.routes = set()

        # 从CSV文件重新加载数据
        df = load_cleaned_data()
        if not df.empty:
            products = create_airline_products(df)
            agent.add_products(products)

            logger.info(f"重新加载完成，共加载 {len(products)} 个产品")

            return {
                "success": True,
                "message": f"重新加载成功，共 {len(products)} 个产品",
                "data": {
                    "count": len(products),
                    "products": [p.to_dict() for p in agent.products]
                }
            }
        else:
            logger.warning("重新加载失败：CSV文件为空")
            return {
                "success": False,
                "message": "重新加载失败：CSV文件为空",
                "data": {"count": 0, "products": []}
            }

    except Exception as e:
        logger.error(f"重新加载产品失败: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"重新加载产品失败: {str(e)}",
            "data": {"count": 0, "products": []}
        }


@app.delete("/api/product/{product_id}")
async def delete_product_api(product_id: str, token: str = Depends(verify_token)):
    """删除产品 - 需要鉴权"""
    try:
        from agents.agent import get_agent_instance
        import pandas as pd
        from pathlib import Path

        agent = get_agent_instance()

        # 找到对应的产品
        deleted_product = None
        deleted_index = -1
        for i, product in enumerate(agent.products):
            if product.product_id == product_id:
                deleted_product = product
                deleted_index = i
                break

        if deleted_product is None:
            return {
                "success": False,
                "message": f"产品ID {product_id} 不存在"
            }

        # 从内存中删除
        agent.products.pop(deleted_index)

        # 更新CSV文件
        csv_path = Path(workspace_path) / "assets" / "products.csv"
        df = pd.read_csv(csv_path, encoding='utf-8-sig')

        # 删除对应的行(基于product_id)
        mask = df['airline'] == deleted_product.airline
        mask &= df['product_name'] == deleted_product.product_name
        mask &= df['route'] == deleted_product.route
        mask &= df['booking_class'] == deleted_product.booking_class
        mask &= df['policy_code'] == deleted_product.policy_code
        mask &= df['office'] == deleted_product.office

        # 找到第一条匹配的记录的索引
        matching_indices = df[mask].index.tolist()

        if matching_indices:
            # 只删除第一条匹配的记录
            first_match_index = matching_indices[0]
            df = df.drop(first_match_index)

        # 保存回CSV文件
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')

        logger.info(f"已删除产品: {deleted_product.airline} - {deleted_product.product_name}")

        return {
            "success": True,
            "message": f"已删除产品: {deleted_product.airline} - {deleted_product.product_name}",
            "data": {
                "deleted_product": deleted_product.to_dict(),
                "remaining_count": len(agent.products)
            }
        }
    except Exception as e:
        logger.error(f"删除产品失败: {e}")
        return {
            "success": False,
            "message": f"删除产品失败: {str(e)}"
        }


@app.put("/api/product/{product_id}")
async def update_product_api(product_id: str, product_data: dict, token: str = Depends(verify_token)):
    """更新产品信息 - 需要鉴权"""
    try:
        from agents.agent import get_agent_instance
        import pandas as pd
        from pathlib import Path

        agent = get_agent_instance()

        # 找到对应的产品
        original_product = None
        for product in agent.products:
            if product.product_id == product_id:
                original_product = product
                break

        if original_product is None:
            return {
                "success": False,
                "message": f"产品ID {product_id} 不存在"
            }

        # 更新产品字段
        update_fields = ['product_name', 'route', 'booking_class', 'price_increase',
                       'rebate_ratio', 'office', 'remarks', 'valid_period',
                       'ticket_type', 'policy_identifier', 'policy_code']

        for field in update_fields:
            if field in product_data:
                setattr(original_product, field, product_data[field])

        # 更新CSV文件
        csv_path = Path(workspace_path) / "assets" / "products.csv"
        df = pd.read_csv(csv_path, encoding='utf-8-sig')

        # 找到并更新对应的行
        mask = df['airline'] == original_product.airline
        mask &= df['product_name'] == original_product.product_name
        mask &= df['route'] == original_product.route
        mask &= df['booking_class'] == original_product.booking_class
        mask &= df['policy_code'] == original_product.policy_code
        mask &= df['office'] == original_product.office

        if mask.any():
            # 更新第一条匹配的记录
            for idx in df[mask].index[:1]:
                for field in update_fields:
                    if field in product_data:
                        df.at[idx, field] = product_data[field]

        # 保存回CSV文件
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')

        logger.info(f"已更新产品: {original_product.airline} - {original_product.product_name}")

        return {
            "success": True,
            "message": f"已更新产品: {original_product.airline} - {original_product.product_name}",
            "data": {
                "updated_product": original_product.to_dict()
            }
        }
    except Exception as e:
        logger.error(f"更新产品失败: {e}")
        return {
            "success": False,
            "message": f"更新产品失败: {str(e)}"
        }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点 - 实时推送数据更新"""
    await manager.connect(websocket)
    try:
        while True:
            # 接收客户端消息（用于心跳等）
            data = await websocket.receive_text()
            # 可以处理客户端发送的消息
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket客户端断开连接")
    except Exception as e:
        logger.error(f"WebSocket错误: {e}", exc_info=True)
        manager.disconnect(websocket)


# ============================================================================
# 文件上传API端点
# ============================================================================

@app.post("/api/upload/file")
async def upload_file(file: UploadFile = File(...), token: str = Depends(verify_token)):
    """
    上传文件并解析 - 需要鉴权

    支持的文件格式：
    - CSV: .csv
    - Excel: .xls, .xlsx
    - PDF: .pdf
    - Word: .doc, .docx
    - 图片: .jpg, .jpeg, .png, .gif, .bmp
    - JSON: .json
    - 文本: .txt

    Returns:
        解析后的文件内容或错误信息
    """
    try:
        from utils.file_parser import parse_file

        # 读取文件内容
        file_content = await file.read()

        # 解析文件
        result = parse_file(file_content=file_content, filename=file.filename)

        # 如果解析失败，返回错误
        if not result.get('success'):
            return {
                "success": False,
                "message": f"文件解析失败: {result.get('error', '未知错误')}",
                "data": {
                    "filename": file.filename,
                    "file_type": result.get('type', 'unknown')
                }
            }

        # 返回解析结果
        return {
            "success": True,
            "message": f"文件解析成功: {file.filename}",
            "data": {
                "filename": file.filename,
                "file_type": result.get('type'),
                "content": result
            }
        }
    except Exception as e:
        logger.error(f"文件上传失败: {e}")
        return {
            "success": False,
            "message": f"文件上传失败: {str(e)}",
            "data": {}
        }


@app.post("/api/upload/products")
async def upload_products_file(file: UploadFile = File(...), token: str = Depends(verify_token)):
    """
    上传产品文件并提取产品数据 - 需要鉴权

    支持的文件格式：
    - CSV: .csv
    - Excel: .xls, .xlsx
    - JSON: .json

    其他格式（PDF、Word、图片）将尝试提取文本，但可能不完整

    Returns:
        提取的产品数据
    """
    try:
        from utils.file_parser import extract_product_data_from_file
        from agents.agent import get_agent_instance
        import csv
        from pathlib import Path

        logger.info(f"开始处理上传文件: {file.filename}, 类型: {file.content_type}")

        # 读取文件内容
        file_content = await file.read()
        logger.info(f"文件大小: {len(file_content)} bytes")

        # 提取产品数据
        result = extract_product_data_from_file(file_content=file_content, filename=file.filename)

        if not result.get('success'):
            error_msg = result.get('error', '未知错误')
            logger.error(f"提取产品数据失败: {error_msg}")
            return {
                "success": False,
                "message": f"提取产品数据失败: {error_msg}",
                "data": {
                    "filename": file.filename,
                    "file_type": result.get('type', 'unknown')
                }
            }

        products = result.get('products', [])
        warning = result.get('warning', '')
        file_type = result.get('type', 'unknown')

        logger.info(f"成功从 {file_type} 文件中提取 {len(products)} 个产品")

        # 获取智能体实例
        agent = get_agent_instance()

        # 添加产品到智能体
        added_count = 0
        skipped_count = 0
        for idx, product_data in enumerate(products):
            # 检查必填字段
            airline = product_data.get('airline', '').strip()
            product_name = product_data.get('product_name', '').strip()

            if not airline or not product_name:
                skipped_count += 1
                logger.warning(f"跳过第 {idx+1} 个产品: 缺少航司代码或产品名称")
                continue

            try:
                from agents.agent import AirlineProduct
                product = AirlineProduct(
                    airline=airline,
                    product_name=product_name,
                    route=product_data.get('route', ''),
                    booking_class=product_data.get('booking_class', ''),
                    price_increase=product_data.get('price_increase', 0),
                    rebate_ratio=product_data.get('rebate_ratio', ''),
                    office=product_data.get('office', ''),
                    remarks=product_data.get('remarks', ''),
                    valid_period=product_data.get('valid_period', ''),
                    ticket_type=product_data.get('ticket_type', 'ALL'),
                    policy_identifier=product_data.get('policy_identifier', ''),
                    policy_code=product_data.get('policy_code', '')
                )
                agent.add_product(product)
                added_count += 1
            except Exception as e:
                logger.error(f"添加第 {idx+1} 个产品失败: {e}")
                skipped_count += 1

        logger.info(f"成功添加 {added_count} 个产品, 跳过 {skipped_count} 个产品")

        # 保存到CSV文件
        workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
        products_file = Path(workspace_path) / "assets" / "products.csv"

        try:
            # 读取现有产品
            existing_products = []
            if products_file.exists():
                with open(products_file, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    existing_products = list(reader)

            # 添加新产品
            fieldnames = ['airline', 'product_name', 'route', 'booking_class',
                         'price_increase', 'rebate_ratio', 'office', 'remarks',
                         'valid_period', 'ticket_type', 'policy_identifier', 'policy_code']

            new_products = []
            for product_data in products:
                # 只保存有效的产品
                if product_data.get('airline', '').strip() and product_data.get('product_name', '').strip():
                    new_products.append({
                        'airline': product_data.get('airline', ''),
                        'product_name': product_data.get('product_name', ''),
                        'route': product_data.get('route', ''),
                        'booking_class': product_data.get('booking_class', ''),
                        'price_increase': product_data.get('price_increase', 0),
                        'rebate_ratio': product_data.get('rebate_ratio', ''),
                        'office': product_data.get('office', ''),
                        'remarks': product_data.get('remarks', ''),
                        'valid_period': product_data.get('valid_period', ''),
                        'ticket_type': product_data.get('ticket_type', 'ALL'),
                        'policy_identifier': product_data.get('policy_identifier', ''),
                        'policy_code': product_data.get('policy_code', '')
                    })

            # 合并并保存
            all_products = existing_products + new_products

            with open(products_file, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_products)

            logger.info(f"已保存 {len(new_products)} 个新产品到 {products_file}")
        except Exception as e:
            logger.warning(f"保存产品到CSV失败: {e}")

        # 返回结果
        message_parts = [f"成功添加 {added_count} 个产品"]
        if skipped_count > 0:
            message_parts.append(f"(跳过 {skipped_count} 个无效产品)")
        if warning:
            message_parts.append(f"\n{warning}")

        # 重新加载产品数据到内存
        try:
            logger.info("开始重新加载产品数据到内存...")
            from agents.agent import load_cleaned_data, create_airline_products

            # 清空现有产品
            agent.products = []
            agent.airlines = set()
            agent.routes = set()

            # 从CSV文件重新加载数据
            df = load_cleaned_data()
            if not df.empty:
                products_reloaded = create_airline_products(df)
                agent.add_products(products_reloaded)
                logger.info(f"重新加载完成，共加载 {len(products_reloaded)} 个产品")
                message_parts.append(f"\n内存中产品数据已更新，共 {len(products_reloaded)} 个产品")
        except Exception as reload_error:
            logger.warning(f"重新加载产品数据到内存失败: {reload_error}")
            message_parts.append(f"\n注意：内存中产品数据未更新")

        return {
            "success": True,
            "message": "。".join(message_parts),
            "data": {
                "filename": file.filename,
                "file_type": file_type,
                "total_products": len(products),
                "added_products": added_count,
                "skipped_products": skipped_count,
                "products": products,
                "warning": warning
            }
        }
    except Exception as e:
        logger.error(f"上传产品文件失败: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"上传产品文件失败: {str(e)}",
            "data": {}
        }


@app.post("/api/upload/preview")
async def upload_and_preview_file(file: UploadFile = File(...), token: str = Depends(verify_token)):
    """
    上传文件并预览内容 - 需要鉴权

    用于在导入产品前预览文件内容
    """
    try:
        from utils.file_parser import extract_product_data_from_file

        # 读取文件内容
        file_content = await file.read()
        file_size = len(file_content)
        logger.info(f"预览文件: {file.filename}, 大小: {file_size} bytes, 内容类型: {file.content_type}")

        # 提取产品数据
        result = extract_product_data_from_file(file_content=file_content, filename=file.filename)

        if not result.get('success'):
            error_msg = result.get('error', '未知错误')
            logger.error(f"文件解析失败: {error_msg}", exc_info=True)
            return {
                "success": False,
                "message": f"文件解析失败: {error_msg}",
                "data": {
                    "filename": file.filename,
                    "file_type": result.get('type', 'unknown')
                }
            }

        products = result.get('products', [])
        warning = result.get('warning', '')

        logger.info(f"预览成功: 提取到 {len(products)} 个产品")

        # 只返回前10个产品用于预览
        preview_products = products[:10]

        # 记录第一个产品的详细信息用于调试
        if preview_products:
            sample = preview_products[0]
            logger.info(f"示例产品: 航司={sample.get('airline')}, 产品={sample.get('product_name')}, "
                       f"上浮={sample.get('price_increase')}, 返点={sample.get('rebate_ratio')}, "
                       f"Office={sample.get('office')}")

        return {
            "success": True,
            "message": f"文件预览成功: {file.filename}",
            "data": {
                "filename": file.filename,
                "file_type": result.get('type'),
                "total_products": len(products),
                "preview_products": preview_products,
                "warning": warning
            }
        }
    except Exception as e:
        logger.error(f"文件预览失败: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"文件预览失败: {str(e)}",
            "data": {}
        }


def parse_args():
    parser = argparse.ArgumentParser(description="Start FastAPI server")
    parser.add_argument("-m", type=str, default="http", help="Run mode, support http,flow,node")
    parser.add_argument("-n", type=str, default="", help="Node ID for single node run")
    parser.add_argument("-p", type=int, default=5000, help="HTTP server port")
    parser.add_argument("-i", type=str, default="", help="Input JSON string for flow/node mode")
    return parser.parse_args()


@app.post("/api/upload/debug")
async def upload_and_debug_file(file: UploadFile = File(...)):
    """
    上传文件并返回详细的调试信息

    用于诊断文件解析问题
    """
    try:
        from utils.file_parser import parse_file

        # 读取文件内容
        file_content = await file.read()

        # 先解析文件结构
        parsed_data = parse_file(file_content=file_content, filename=file.filename)

        debug_info = {
            "filename": file.filename,
            "file_size": len(file_content),
            "file_type": parsed_data.get('type', 'unknown'),
            "parse_success": parsed_data.get('success', False),
        }

        if not parsed_data.get('success'):
            debug_info["error"] = parsed_data.get('error', '解析失败')
            return {
                "success": False,
                "message": "文件解析失败",
                "data": debug_info
            }

        # 提取列名和前几行数据
        if parsed_data.get('type') == 'csv':
            debug_info["headers"] = parsed_data.get('headers', [])
            debug_info["total_rows"] = parsed_data.get('total_rows', 0)
            # 显示前5行数据
            debug_info["sample_rows"] = parsed_data.get('rows', [])[:5]
        elif parsed_data.get('type') == 'excel':
            sheets = parsed_data.get('sheets', {})
            debug_info["sheets"] = {}
            for sheet_name, sheet_data in sheets.items():
                debug_info["sheets"][sheet_name] = {
                    "headers": sheet_data.get('headers', []),
                    "total_rows": sheet_data.get('total_rows', 0),
                    "sample_rows": sheet_data.get('rows', [])[:3]
                }

        # 尝试提取产品
        from utils.file_parser import extract_product_data_from_file
        result = extract_product_data_from_file(file_content=file_content, filename=file.filename)

        debug_info["extract_success"] = result.get('success', False)
        if result.get('success'):
            debug_info["total_products"] = len(result.get('products', []))
            debug_info["warning"] = result.get('warning', '')
            if result.get('products'):
                debug_info["sample_products"] = result['products'][:3]
        else:
            debug_info["extract_error"] = result.get('error', '提取失败')

        return {
            "success": True,
            "message": "调试信息获取成功",
            "data": debug_info
        }
    except Exception as e:
        logger.error(f"获取调试信息失败: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"获取调试信息失败: {str(e)}",
            "data": {}
        }


def parse_input(input_str: str) -> Dict[str, Any]:
    """Parse input string, support both JSON string and plain text"""
    if not input_str:
        return {"text": "你好"}

    # Try to parse as JSON first
    try:
        return json.loads(input_str)
    except json.JSONDecodeError:
        # If not valid JSON, treat as plain text
        return {"text": input_str}

def on_products_file_changed(file_path):
    """产品文件变化回调函数"""
    try:
        logger.info(f"检测到产品文件变化: {file_path}")

        # 重新加载数据
        from agents.agent import get_agent_instance
        agent = get_agent_instance()
        agent.load_products()  # 重新加载产品数据

        # 通知所有WebSocket连接数据已更新
        asyncio.create_task(notify_data_updated("产品文件已更新，数据已自动刷新"))

        logger.info("产品数据已重新加载并通知所有客户端")
    except Exception as e:
        logger.error(f"重新加载产品数据失败: {e}", exc_info=True)


def start_http_server(port):
    workers = 1
    reload = False
    if graph_helper.is_dev_env():
        reload = True

    # 确保 utils 模块可以被找到
    import sys
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    if workspace_path not in sys.path:
        sys.path.insert(0, workspace_path)

    # 启动文件监控
    products_csv_path = os.path.join(workspace_path, "assets", "products.csv")
    if os.path.exists(products_csv_path):
        start_file_watcher(products_csv_path, on_products_file_changed)
        logger.info(f"已启动产品文件监控: {products_csv_path}")
    else:
        logger.warning(f"产品文件不存在，不启动文件监控: {products_csv_path}")

    logger.info(f"Start HTTP Server, Port: {port}, Workers: {workers}")
    logger.info(f"🔗 访问地址: http://localhost:{port}")
    logger.info(f"🔑 登录账号: {AUTH_USERNAME} / {AUTH_PASSWORD}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=reload, workers=workers)

if __name__ == "__main__":
    args = parse_args()
    if args.m == "http":
        start_http_server(args.p)
    elif args.m == "flow":
        payload = parse_input(args.i)
        result = asyncio.run(service.run(payload))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.m == "node" and args.n:
        payload = parse_input(args.i)
        result = asyncio.run(service.run_node(args.n, payload))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.m == "agent":
        agent_ctx = new_context(method="agent")
        for chunk in service.stream(
                {
                    "type": "query",
                    "session_id": "1",
                    "message": "你好",
                    "content": {
                        "query": {
                            "prompt": [
                                {
                                    "type": "text",
                                    "content": {"text": "现在几点了？请调用工具获取当前时间"},
                                }
                            ]
                        }
                    },
                },
                run_config={"configurable": {"session_id": "1"}},
                ctx=agent_ctx,
        ):
            print(chunk)
