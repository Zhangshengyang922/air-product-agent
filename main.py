#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简化版航空公司产品智能体系统 (CloudStudio部署版本)
内嵌HTML前端,无需静态文件
"""

import pandas as pd
import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# 创建FastAPI应用
app = FastAPI(title="航空公司产品智能体", version="1.0.0")

# 挂载静态文件目录
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# 大客户政策页面路由
@app.get("/vip_clients.html")
async def vip_clients_page():
    """大客户政策页面"""
    vip_file = static_path / "vip_clients.html"
    if vip_file.exists():
        return HTMLResponse(content=vip_file.read_text(encoding='utf-8'))
    return HTMLResponse(content="<h1>页面不存在</h1>", status_code=404)

# index.html 页面路由
@app.get("/index.html")
async def index_html_page():
    """index.html页面"""
    index_file = static_path / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding='utf-8'))
    return HTMLResponse(content="<h1>页面不存在</h1>", status_code=404)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# 数据加载
# ============================================================================

class Product:
    """产品数据模型（新格式5.28）"""
    def __init__(self, airline, airline_name='', product_name='', route='', booking_class='', 
                 price_increase='', rebate_ratio='', office='', remarks='', valid_period='', 
                 policy_code='', settlement='', ticket_type='',
                 front_rebate_type='', front_rebate_value='',
                 back_rebate_type='', back_rebate_value='',
                 fixed_agent_fee='', valid_start='', valid_end='',
                 creator='', create_time=''):
        self.airline = airline
        self.airline_name = airline_name
        self.product_name = product_name
        self.route = route
        self.booking_class = booking_class
        self.price_increase = price_increase
        self.rebate_ratio = rebate_ratio
        self.office = office
        self.remarks = remarks
        self.valid_period = valid_period
        self.policy_code = policy_code
        self.settlement = settlement
        self.ticket_type = ticket_type
        # 新格式字段
        self.front_rebate_type = front_rebate_type
        self.front_rebate_value = front_rebate_value
        self.back_rebate_type = back_rebate_type
        self.back_rebate_value = back_rebate_value
        self.fixed_agent_fee = fixed_agent_fee
        self.valid_start = valid_start
        self.valid_end = valid_end
        self.creator = creator
        self.create_time = create_time

    def to_dict(self):
        return {
            'airline': self.airline,
            'airline_name': self.airline_name,
            'product_name': self.product_name,
            'route': self.route,
            'booking_class': self.booking_class,
            'price_increase': self.price_increase,
            'rebate_ratio': self.rebate_ratio,
            'office': self.office,
            'remarks': self.remarks,
            'valid_period': self.valid_period,
            'policy_code': self.policy_code,
            'settlement': self.settlement,
            'ticket_type': self.ticket_type,
            'front_rebate_type': self.front_rebate_type,
            'front_rebate_value': self.front_rebate_value,
            'back_rebate_type': self.back_rebate_type,
            'back_rebate_value': self.back_rebate_value,
            'fixed_agent_fee': self.fixed_agent_fee,
            'valid_start': self.valid_start,
            'valid_end': self.valid_end,
            'creator': self.creator,
            'create_time': self.create_time
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

        # 检测CSV格式（新格式用"航司"，旧格式用"航司代码"）
        airline_col = '航司' if '航司' in df.columns else '航司代码'

        # 记录航司出现顺序（跳过说明文字行）
        airline_order = []
        for idx, airline in enumerate(df[airline_col]):
            airline_str = str(airline).strip()
            if airline_str and not airline_str.startswith('（') and not airline_str.startswith('(') and airline_str not in airline_order:
                if len(airline_str) > 2 and airline_str[0].isdigit() and airline_str[1] in '、.':
                    continue
                airline_order.append(airline_str)

        # 构建前返/后返显示字符串
        def build_rebate(row):
            parts = []
            ft = str(row.get('前返计算方式', '')).strip()
            fv = str(row.get('前返计算值', '')).strip()
            bt = str(row.get('后返计算方式', '')).strip()
            bv = str(row.get('后返计算值', '')).strip()
            af = str(row.get('定额代理费', '')).strip()
            if ft and fv:
                parts.append(f"前返{ft}{fv}")
            elif fv:
                parts.append(fv)
            if bt and bv:
                parts.append(f"后返{bt}{bv}")
            elif bv:
                parts.append(bv)
            if af:
                parts.append(f"定额{af}")
            if parts:
                return '+'.join(parts)
            # 兼容旧格式
            return str(row.get('政策返点', '')).strip()

        def build_settlement(row):
            parts = []
            ft = str(row.get('前返计算方式', '')).strip()
            bt = str(row.get('后返计算方式', '')).strip()
            af = str(row.get('定额代理费', '')).strip()
            if ft: parts.append(f"前返-{ft}")
            if bt: parts.append(f"后返-{bt}")
            if af: parts.append(f"定额-{af}")
            if parts:
                return '+'.join(parts)
            return str(row.get('航司结算方式', '')).strip()

        products = []
        for idx, row in df.iterrows():
            try:
                airline = str(row.get(airline_col, '')).strip()
                airline_name = str(row.get('航司名称', '')).strip()
                product_name = str(row.get('产品名称', '')).strip()
                route = str(row.get('航线', '')).strip()
                booking_class = str(row.get('订座舱位', '')).strip()
                price_increase = str(row.get('上浮价格', '')).strip()
                rebate_ratio = build_rebate(row)
                office = str(row.get('出票OFFICE', '')).strip()
                remarks = str(row.get('备注', '')).strip()
                # 新格式：有效开始日期 + 有效截止日期；旧格式：产品有限期
                valid_start = str(row.get('有效开始日期', '')).strip()
                valid_end = str(row.get('有效截止日期', '')).strip()
                if valid_start or valid_end:
                    valid_period = f"{valid_start} 至 {valid_end}".strip(' 至 ')
                else:
                    valid_period = str(row.get('产品有限期', '')).strip()
                policy_code_val = row.get('运价标识', row.get('产品代码', ''))
                policy_code = str(policy_code_val).strip() if pd.notna(policy_code_val) else ''
                settlement = build_settlement(row)
                ticket_type = str(row.get('票证类型', '')).strip()
                # 新格式字段
                front_rebate_type = str(row.get('前返计算方式', '')).strip()
                front_rebate_value = str(row.get('前返计算值', '')).strip()
                back_rebate_type = str(row.get('后返计算方式', '')).strip()
                back_rebate_value = str(row.get('后返计算值', '')).strip()
                fixed_agent_fee = str(row.get('定额代理费', '')).strip()
                creator = str(row.get('创建人', '')).strip()
                create_time = str(row.get('创建时间', '')).strip()

                if product_name and airline and not airline.startswith('（') and not airline.startswith('('):
                    if len(airline) > 2 and airline[0].isdigit() and airline[1] in '、.':
                        continue
                    
                    product = Product(
                        airline=airline,
                        airline_name=airline_name,
                        product_name=product_name,
                        route=route,
                        booking_class=booking_class,
                        price_increase=price_increase,
                        rebate_ratio=rebate_ratio,
                        office=office,
                        remarks=remarks,
                        valid_period=valid_period,
                        policy_code=policy_code,
                        settlement=settlement,
                        ticket_type=ticket_type,
                        front_rebate_type=front_rebate_type,
                        front_rebate_value=front_rebate_value,
                        back_rebate_type=back_rebate_type,
                        back_rebate_value=back_rebate_value,
                        fixed_agent_fee=fixed_agent_fee,
                        valid_start=valid_start,
                        valid_end=valid_end,
                        creator=creator,
                        create_time=create_time
                    )
                    # 添加原始顺序属性
                    product._original_order = idx
                    products.append(product)
                    airlines_set.add(airline)
            except Exception as e:
                print(f"[X] 处理行失败: {e}")
                continue

        print(f"[OK] 成功加载 {len(products)} 个产品")
        print(f"[OK] 识别到 {len(airlines_set)} 个航司")
        print(f"[OK] 航司顺序: {', '.join(airline_order[:10])}...")

    except Exception as e:
        print(f"[X] 加载产品数据失败: {e}")

# 全局航司顺序
AIRLINE_ORDER = []

def get_airline_order():
    """获取航司顺序"""
    global AIRLINE_ORDER
    if not AIRLINE_ORDER:
        project_root = Path(__file__).parent
        products_file = project_root / "assets" / "products.csv"
        try:
            df = pd.read_csv(products_file, encoding='utf-8-sig')
            df = df.fillna('')
            for airline in df['航司代码']:
                if airline not in AIRLINE_ORDER and str(airline).strip():
                    AIRLINE_ORDER.append(str(airline).strip())
        except Exception as e:
            print(f"[WARN] 获取航司顺序失败: {e}")
    return AIRLINE_ORDER

# 启动时加载数据
@app.on_event("startup")
async def startup_event():
    """应用启动时加载数据"""
    print("="*60)
    print("航空公司产品智能体系统启动中...")
    print("="*60)
    print(f"[INFO] 当前工作目录: {os.getcwd()}")
    print(f"[INFO] 脚本位置: {Path(__file__).parent}")

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
    '3U': '四川航空', '8L': '祥鹏航空', '9H': '长安航空',
    'A6': '湖南航空', 'BK': '奥凯航空', 'CA': '国航',
    'CJ': '长龙航空', 'CZ': '南航', 'DR': '瑞丽航空', 'DZ': '东海航空',
    'EU': '成都航空', 'FU': '福州航空', 'G5': '华夏航空',
    'GJ': '长龙航空', 'GS': '天津航空', 'GX': '北部湾航空',
    'HO': '吉祥航空', 'HU': '海南航空', 'JD': '首都航空',
    'JR': '幸福航空', 'KY': '昆明航空', 'MF': '厦门航空',
    'MU': '东航', 'NS': '河北航空', 'PN': '西部航空',
    'QW': '青岛航空', 'RY': '江西航空', 'SC': '山东航空',
    'TV': '西藏航空', 'UQ': '乌鲁木齐航空', 'ZH': '深圳航空'
}

# ============================================================================
# API路由
# ============================================================================

# 不再使用硬编码HTML模板，始终从 static/index.html 读取
# 如果 static/index.html 不存在，显示错误提示

@app.get("/")
@app.head("/")
async def index():
    """首页 - 始终从 static/index.html 读取最新版本"""
    index_file = static_path / "index.html"
    print(f"[INDEX] static_path={static_path}, index_file={index_file}, exists={index_file.exists()}")
    
    if index_file.exists():
        content = index_file.read_text(encoding='utf-8')
        print(f"[INDEX] Serving {index_file}, size={len(content)} bytes, has_old='查阅记录' in content={('查阅记录' in content)}")
        return HTMLResponse(content=content, headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        })
    else:
        print(f"[INDEX] ERROR: static/index.html not found at {index_file}")
        return HTMLResponse(content=f'<h1 style="color:red;text-align:center;margin-top:100px">❌ 页面文件未找到</h1><p style="text-align:center">文件路径: {index_file}</p><p style="text-align:center">请确保 static/index.html 文件存在</p>', status_code=500, headers={
            "Cache-Control": "no-cache, no-store, must-revalidate"
        })

from fastapi import Request

@app.post("/api/login")
async def login(request: Request):
    """登录验证"""
    try:
        data = await request.json()
        username = data.get('username', '').strip()
        password = data.get('password', '')

        # 验证账号密码
        if username == 'YNTB' and password == 'yntb123':
            # 生成token（简化版，固定token）
            token = "yntb-auth-token-123456"
            return {"success": True, "token": token, "message": "登录成功"}
        else:
            return {"success": False, "message": "账号或密码错误"}

    except Exception as e:
        return {"success": False, "message": "登录请求失败"}

@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok", "total_products": len(products), "total_airlines": len(airlines_set)}

class ProductsResponse(BaseModel):
    success: bool
    data: Dict

@app.get("/api/airlines/{airline_code}")
async def get_products_by_airline(airline_code: str):
    """根据航司代码获取产品（无需认证）- 按原始顺序"""
    filtered_products = [p for p in products if p.airline == airline_code]

    # 按原始行号排序
    sorted_products = sorted(filtered_products, key=lambda x: getattr(x, '_original_order', 0))

    return ProductsResponse(
        success=True,
        data={
            "products": [p.to_dict() for p in sorted_products],
            "total": len(sorted_products)
        }
    )

@app.get("/api/products", response_model=ProductsResponse)
async def get_all_products(
    airline: Optional[str] = Query(None, description="航司代码"),
    limit: int = Query(0, description="返回数量限制，0=不限制")
):
    """获取所有产品（无需认证）- 按原始顺序"""
    filtered_products = products

    if airline and airline != 'all':
        filtered_products = [p for p in products if p.airline == airline]

    # 按原始行号排序
    sorted_products = sorted(filtered_products, key=lambda x: getattr(x, '_original_order', 0))

    if limit > 0:
        sorted_products = sorted_products[:limit]

    return ProductsResponse(
        success=True,
        data={
            "products": [p.to_dict() for p in sorted_products],
            "total": len(sorted_products)
        }
    )

@app.get("/api/airlines")
async def get_airlines():
    """获取所有航司（无需认证）- 按原始顺序"""
    airline_order = get_airline_order()
    airlines_list = []

    # 按照CSV中的原始顺序添加航司
    for code in airline_order:
        if code in airlines_set:
            name = AIRLINE_NAMES.get(code, code)
            airlines_list.append({
                'code': code,
                'name': name,
                'count': len([p for p in products if p.airline == code]),
                'order': airline_order.index(code)
            })

    # 添加剩余的航司（如果有的话）
    for code in sorted(airlines_set):
        if code not in airline_order:
            name = AIRLINE_NAMES.get(code, code)
            airlines_list.append({
                'code': code,
                'name': name,
                'count': len([p for p in products if p.airline == code]),
                'order': 999
            })

    return {
        "success": True,
        "data": {
            "airlines": airlines_list
        }
    }

@app.get("/api/jd-products")
async def get_jd_products():
    """获取首都航空JD产品"""
    static_dir = Path(__file__).parent / "static"
    jd_file = static_dir / "各航司汇总产品-JD.csv"
    
    jd_products = []
    if jd_file.exists():
        try:
            df = pd.read_csv(jd_file, encoding='utf-8-sig')
            df = df.fillna('')
            for _, row in df.iterrows():
                jd_products.append({
                    "product_name": row.get('产品名称', ''),
                    "route": row.get('航线', ''),
                    "cabin": row.get('订座舱位', ''),
                    "price": row.get('上浮价格/直减', ''),
                    "rebate": row.get('政策返点', ''),
                    "product_code": row.get('产品代码', ''),
                    "office": row.get('出票OFFICE', ''),
                    "remark": row.get('备注', ''),
                    "valid_period": row.get('产品有限期', ''),
                    "settlement": row.get('航司结算方式', '')
                })
        except Exception as e:
            print(f"[ERROR] 加载JD产品失败: {e}")
    
    return {
        "success": True,
        "data": {
            "products": jd_products,
            "total": len(jd_products)
        }
    }

@app.get("/api/search")
async def search_products(
    keyword: str = Query(..., description="搜索关键词")
):
    """搜索产品"""
    keyword = keyword.lower()
    results = []

    for p in products:
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

@app.post("/api/sync/reload")
async def reload_products():
    """重新加载产品数据"""
    try:
        global products, airlines_set
        old_count = len(products)
        load_products()
        new_count = len(products)

        return {
            "success": True,
            "message": "数据重新加载成功",
            "data": {
                "old_count": old_count,
                "new_count": new_count,
                "diff": new_count - old_count
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"重新加载失败: {str(e)}"
        }

@app.get("/api/sync/status")
async def get_sync_status():
    """获取数据同步状态"""
    import json
    from pathlib import Path
    from datetime import datetime

    status_file = Path(__file__).parent / "assets" / "sync_status.json"

    if status_file.exists():
        with open(status_file, 'r', encoding='utf-8') as f:
            status = json.load(f)

        # 计算距离上次同步的时间
        try:
            last_sync = datetime.fromisoformat(status['last_sync_time'])
            diff = datetime.now() - last_sync
            hours_ago = diff.total_seconds() / 3600
            status['hours_ago'] = round(hours_ago, 1)
        except:
            status['hours_ago'] = None

        return {
            "success": True,
            "data": status
        }
    else:
        return {
            "success": False,
            "message": "暂无同步记录"
        }

# ============================================================================
# 启动服务器
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
