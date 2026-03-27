#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简化版航空公司产品智能体系统 (CloudStudio部署版本)
移除了coze-loop等内部依赖,只保留基本的Web界面和产品查询功能
"""

import pandas as pd
import json
import os
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# 创建FastAPI应用
app = FastAPI(title="航空公司产品智能体", version="1.0.0")

# 登录配置
AUTH_USERNAME = "YNTB"
AUTH_PASSWORD = "yntb123"
AUTH_TOKEN_EXPIRE_HOURS = 24

# 存储有效的token
active_tokens: Dict[str, datetime] = {}

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
static_dir = Path(__file__).parent / "static"
print(f"[INFO] 静态文件目录: {static_dir}")
print(f"[INFO] 目录是否存在: {static_dir.exists()}")

# 尝试挂载静态文件
if static_dir.exists():
    try:
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        print(f"[OK] 静态文件挂载成功")
    except Exception as e:
        print(f"[WARN] 静态文件挂载失败: {e}")
else:
    print(f"[WARN] 静态文件目录不存在: {static_dir}")

# ============================================================================
# 数据加载
# ============================================================================

class Product:
    """产品数据模型"""
    def __init__(self, airline, product_name, route, booking_class, price_increase, rebate_ratio, policy_code, ticket_type, office, remarks, valid_period):
        self.airline = airline
        self.product_name = product_name
        self.route = route
        self.booking_class = booking_class
        self.price_increase = price_increase
        self.rebate_ratio = rebate_ratio
        self.policy_code = policy_code
        self.ticket_type = ticket_type
        self.office = office
        self.remarks = remarks
        self.valid_period = valid_period

    def to_dict(self):
        return {
            'airline': self.airline,
            'product_name': self.product_name,
            'route': self.route,
            'booking_class': self.booking_class,
            'price_increase': self.price_increase,
            'rebate_ratio': self.rebate_ratio,
            'policy_code': self.policy_code,
            'ticket_type': self.ticket_type,
            'office': self.office,
            'remarks': self.remarks,
            'valid_period': self.valid_period
        }

# 全局数据存储
products: List[Product] = []
airlines_set = set()

def load_products():
    """加载产品数据"""
    global products, airlines_set

    project_root = Path(__file__).parent
    products_file = project_root / "assets" / "products.csv"

    if not products_file.exists():
        print(f"[WARN] 产品文件不存在: {products_file}")
        return

    try:
        df = pd.read_csv(products_file, encoding='utf-8-sig')
        df = df.fillna('')

        print(f"[OK] 从CSV加载了 {len(df)} 行数据")

        products = []
        for _, row in df.iterrows():
            try:
                airline = str(row.get('航司代码', '')).strip()
                product_name = str(row.get('产品名称', '')).strip()
                route = str(row.get('航线', '')).strip()
                booking_class = str(row.get('订座舱位', '')).strip()
                price_increase = str(row.get('上浮价格', '')).strip()
                rebate_ratio = str(row.get('政策返点', '')).strip()
                policy_code = str(row.get('产品代码', '')).strip()
                ticket_type = 'ALL'  # 默认为 ALL，如果CSV中没有票证类型字段
                office = str(row.get('出票OFFICE', '')).strip()
                remarks = str(row.get('备注', '')).strip()
                valid_period = str(row.get('产品有限期', '')).strip()

                if product_name and airline:
                    product = Product(
                        airline=airline,
                        product_name=product_name,
                        route=route,
                        booking_class=booking_class,
                        price_increase=price_increase,
                        rebate_ratio=rebate_ratio,
                        policy_code=policy_code,
                        ticket_type=ticket_type,
                        office=office,
                        remarks=remarks,
                        valid_period=valid_period
                    )
                    products.append(product)
                    airlines_set.add(airline)
            except Exception as e:
                print(f"[X] 处理行失败: {e}")
                continue

        print(f"[OK] 成功加载 {len(products)} 个产品")
        print(f"[OK] 识别到 {len(airlines_set)} 个航司")

    except Exception as e:
        print(f"[X] 加载产品数据失败: {e}")

# 启动时加载数据
@app.on_event("startup")
async def startup_event():
    """应用启动时加载数据"""
    print("="*60)
    print("航空公司产品智能体系统启动中...")
    print("="*60)
    print(f"[INFO] 当前工作目录: {os.getcwd()}")
    print(f"[INFO] 脚本位置: {Path(__file__).parent}")
    print(f"[INFO] 静态文件目录: {static_dir}")

    # 检查关键文件
    assets_file = Path(__file__).parent / "assets" / "products.csv"
    print(f"[INFO] 产品数据文件: {assets_file}")
    print(f"[INFO] 产品数据文件存在: {assets_file.exists()}")

    load_products()
    print("="*60)
    print("系统启动完成!")
    print("="*60)

# ============================================================================
# 航司名称映射
# ============================================================================

AIRLINE_NAMES = {
    'CA': '中国国际航空', 'MU': '中国东方航空', 'CZ': '中国南方航空', 'HU': '海南航空',
    'FM': '上海航空', 'MF': '厦门航空', 'SC': '山东航空', 'ZH': '深圳航空',
    '3U': '四川航空', 'KY': '昆明航空', 'BK': '奥凯航空', 'CN': '大新华航空',
    'EU': '成都航空', 'G5': '华夏航空', 'GS': '天津航空', 'HO': '吉祥航空',
    'JD': '首都航空', 'JR': '幸福航空', 'KN': '中国联合航空', 'NS': '河北航空',
    'OQ': '重庆航空', 'QW': '青岛航空', 'RY': '江西航空', 'TV': '西藏航空',
    'UQ': '乌鲁木齐航空', 'PN': '西部航空', '8L': '祥鹏航空', '9H': '长安航空',
    'A6': '红土航空', 'DR': '桂林航空', 'FU': '福州航空', 'GJ': '长龙航空',
    'GX': '北部湾航空', 'DZ': '东海航空', 'LT': '龙江航空', 'GY': '多彩贵州'
}

# ============================================================================
# 登录相关
# ============================================================================

def generate_token() -> str:
    """生成简单的token"""
    return str(uuid.uuid4())

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

@app.get("/")
@app.head("/")
async def root(request: Request):
    """主页,返回登录界面"""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    else:
        return {"message": "Airline Product System", "status": "running"}

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
        print(f"登录错误: {str(e)}")
        return JSONResponse({
            "success": False,
            "message": "登录失败,请稍后重试"
        }, status_code=500)

# ============================================================================
# API路由
# ============================================================================

@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok", "total_products": len(products), "total_airlines": len(airlines_set)}

@app.get("/api/airlines")
async def get_airlines(request: Request):
    """获取所有航空公司"""
    token = verify_token_optional(request)
    if not token:
        return JSONResponse({
            "success": False,
            "message": "请先登录"
        }, status_code=401)

    airlines = sorted([{
        "code": code,
        "name": AIRLINE_NAMES.get(code, code),
        "count": len([p for p in products if p.airline == code])
    } for code in airlines_set], key=lambda x: x['code'])

    return {
        "success": True,
        "data": {
            "airlines": airlines
        }
    }

@app.get("/api/airlines/{airline_code}")
async def get_airline_products(airline_code: str, request: Request):
    """获取指定航空公司的产品"""
    token = verify_token_optional(request)
    if not token:
        return JSONResponse({
            "success": False,
            "message": "请先登录"
        }, status_code=401)

    filtered_products = [p for p in products if p.airline == airline_code]

    return {
        "success": True,
        "data": {
            "airline": airline_code,
            "airline_name": AIRLINE_NAMES.get(airline_code, airline_code),
            "products": [p.to_dict() for p in filtered_products],
            "total": len(filtered_products)
        }
    }

class ProductsResponse(BaseModel):
    success: bool
    data: Dict

@app.get("/api/products", response_model=ProductsResponse)
async def get_all_products(
    airline: Optional[str] = Query(None, description="航司代码"),
    limit: int = Query(100, description="返回数量限制")
):
    """获取所有产品"""
    filtered_products = products

    if airline and airline != 'all':
        filtered_products = [p for p in products if p.airline == airline]

    if limit > 0:
        filtered_products = filtered_products[:limit]

    return ProductsResponse(
        success=True,
        data={
            "products": [p.to_dict() for p in filtered_products],
            "total": len(filtered_products)
        }
    )

@app.get("/api/search")
async def search_products(
    keyword: str = Query(..., description="搜索关键词")
):
    """搜索产品"""
    keyword = keyword.lower()
    results = []

    for p in products:
        # 在产品名称、航线、舱位中搜索
        if (keyword in p.product_name.lower() or
            keyword in p.route.lower() or
            keyword in p.booking_class.lower() or
            keyword in p.airline.lower()):
            results.append(p.to_dict())

    return {
        "success": True,
        "data": {
            "products": results,
            "total": len(results)
        }
    }

@app.get("/api/airline/{airline_code}")
async def get_products_by_airline(airline_code: str):
    """根据航司代码获取产品"""
    airline_products = [p for p in products if p.airline == airline_code.upper()]

    if not airline_products:
        raise HTTPException(status_code=404, detail=f"未找到航司 {airline_code} 的产品")

    return {
        "success": True,
        "data": {
            "airline": airline_code,
            "airline_name": AIRLINE_NAMES.get(airline_code, airline_code),
            "products": [p.to_dict() for p in airline_products],
            "total": len(airline_products)
        }
    }

@app.get("/api/stats")
async def get_statistics():
    """获取统计信息"""
    stats = {
        "total_products": len(products),
        "total_airlines": len(airlines_set),
        "products_by_airline": {}
    }

    for code in sorted(airlines_set):
        count = len([p for p in products if p.airline == code])
        name = AIRLINE_NAMES.get(code, code)
        stats["products_by_airline"][code] = {
            "name": name,
            "count": count
        }

    return {
        "success": True,
        "data": stats
    }

# ============================================================================
# 启动服务器
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5173,
        log_level="info"
    )
