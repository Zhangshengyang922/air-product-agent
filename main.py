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
    """产品数据模型"""
    def __init__(self, airline, product_name, route, booking_class, price_increase, rebate_ratio, office, remarks, valid_period, policy_code, settlement=''):
        self.airline = airline
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

    def to_dict(self):
        return {
            'airline': self.airline,
            'product_name': self.product_name,
            'route': self.route,
            'booking_class': self.booking_class,
            'price_increase': self.price_increase,
            'rebate_ratio': self.rebate_ratio,
            'office': self.office,
            'remarks': self.remarks,
            'valid_period': self.valid_period,
            'policy_code': self.policy_code,
            'settlement': self.settlement
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

        # 记录航司出现顺序（跳过说明文字行）
        airline_order = []
        for idx, airline in enumerate(df['航司代码']):
            airline_str = str(airline).strip()
            # 跳过空行和说明文字行（以中文括号开头，或说明文字如"1、xxx"）
            if airline_str and not airline_str.startswith('（') and not airline_str.startswith('(') and airline_str not in airline_order:
                # 跳过说明文字（以数字序号开头且后面是中文的，如"1、机+积分"）
                if len(airline_str) > 2 and airline_str[0].isdigit() and airline_str[1] in '、.':
                    continue
                airline_order.append(airline_str)

        products = []
        for idx, row in df.iterrows():
            try:
                airline = str(row.get('航司代码', '')).strip()
                product_name = str(row.get('产品名称', '')).strip()
                route = str(row.get('航线', '')).strip()
                booking_class = str(row.get('订座舱位', '')).strip()
                price_increase = str(row.get('上浮价格', '')).strip()
                rebate_ratio = str(row.get('政策返点', '')).strip()
                office = str(row.get('出票OFFICE', '')).strip()
                remarks = str(row.get('备注', '')).strip()
                valid_period = str(row.get('产品有限期', '')).strip()
                policy_code_val = row.get('产品代码', '')
                policy_code = str(policy_code_val).strip() if pd.notna(policy_code_val) else ''

                if product_name and airline and not airline.startswith('（') and not airline.startswith('('):
                    # 跳过说明文字（以数字序号开头且后面是中文的，如"1、机+积分"）
                    if len(airline) > 2 and airline[0].isdigit() and airline[1] in '、.':
                        continue
                    # 读取结算方式
                    settlement = str(row.get('航司结算方式', '')).strip()
                    
                    # 添加原始行号用于排序
                    product = Product(
                        airline=airline,
                        product_name=product_name,
                        route=route,
                        booking_class=booking_class,
                        price_increase=price_increase,
                        rebate_ratio=rebate_ratio,
                        office=office,
                        remarks=remarks,
                        valid_period=valid_period,
                        policy_code=policy_code,
                        settlement=settlement
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
    'A6': '红土航空', 'BK': '奥凯航空', 'CA': '国航',
    'CZ': '南航', 'DR': '桂林航空', 'DZ': '东海航空',
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

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>航空公司产品智能体</title>
    <!-- Element UI -->
    <link rel="stylesheet" href="https://unpkg.com/element-ui/lib/theme-chalk/index.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Microsoft YaHei', Arial, sans-serif; background: #f5f7fa; min-height: 100vh; }
        #app { min-height: 100vh; }
        .login-container { display: flex; justify-content: center; align-items: center; min-height: 100vh; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .login-box { background: white; border-radius: 8px; padding: 40px; width: 400px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
        .login-title { font-size: 24px; text-align: center; margin-bottom: 30px; color: #333; }
        .main-container { min-height: 100vh; padding: 20px; }
        .main-content { max-width: 1600px; margin: 0 auto; }
        .content-header { background: white; padding: 20px; border-radius: 4px; margin-bottom: 15px; }
        .header-title { font-size: 18px; font-weight: bold; color: #303133; margin-bottom: 15px; }
        .header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .filter-row { display: flex; gap: 15px; flex-wrap: wrap; align-items: center; }
        .filter-row .el-select, .filter-row .el-input { width: 150px; }
        .data-panel { background: white; padding: 10px; border-radius: 4px; }
        .upload-btn { display: inline-block; padding: 10px 20px; background: #409eff; color: white; border-radius: 4px; font-size: 13px; text-decoration: none; }
        .tag-price { background: #409eff; color: white; padding: 2px 8px; border-radius: 3px; font-size: 12px; font-weight: bold; }
        .el-table { font-size: 12px; }
        .el-table .cell { white-space: normal; line-height: 1.3; padding: 0 5px; }
        .el-table th { padding: 6px 0; background: #f5f7fa; height: 36px; }
        .el-table td { padding: 4px 0; height: 36px; }
        .el-table th .cell, .el-table td .cell { line-height: 1.3; }
        .tag-type { padding: 2px 8px; border-radius: 3px; font-size: 11px; }
        .tag-type.ALL { background: #e6a23c; color: white; }
        .tag-type.GP { background: #67c23a; color: white; }
        .tag-type.BSP { background: #909399; color: white; }
        .tag-type.B2B { background: #f56c6c; color: white; }
        .tag-new { background: #f56c6c; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px; margin-left: 5px; }
    </style>
</head>
<body>
    <div id="app">
        <!-- 登录页 -->
        <div v-if="!isLoggedIn" class="login-container">
            <div class="login-box">
                <div class="login-title">✈️ 航空公司产品系统</div>
                <el-form @submit.native.prevent="handleLogin">
                    <el-form-item>
                        <el-input v-model="loginForm.username" placeholder="账号" prefix-icon="el-icon-user"></el-input>
                    </el-form-item>
                    <el-form-item>
                        <el-input v-model="loginForm.password" type="password" placeholder="密码" prefix-icon="el-icon-lock" @keyup.enter.native="handleLogin"></el-input>
                    </el-form-item>
                    <el-form-item>
                        <el-button type="primary" style="width:100%" :loading="loginLoading" @click="handleLogin">登 录</el-button>
                    </el-form-item>
                    <div v-if="loginError" style="color:#f56c6c;text-align:center;font-size:13px">{{loginError}}</div>
                </el-form>
            </div>
        </div>

        <!-- 主界面 -->
        <div v-else class="main-container">
            <div class="main-content">
                <div class="content-header">
                    <div class="header-row">
                        <div class="header-title">
                            {{selectedAirline ? getAirlineName(selectedAirline) + ' 产品' : '全部产品'}}
                            <span style="font-size:14px;color:#909399;font-weight:normal">({{products.length}}条)</span>
                        </div>
                        <div>
                            <a href="/vip_clients.html" class="upload-btn" style="background:#67c23a;margin-right:10px">🏢 大客户政策</a>
                            <a href="/upload.html" class="upload-btn">📤 上传产品</a>
                        </div>
                    </div>
                    <div class="filter-row">
                        <el-select v-model="selectedAirline" placeholder="选择航空公司" clearable size="small" filterable>
                            <el-option label="全部航司" value=""></el-option>
                            <el-option v-for="airline in allAirlines" :key="airline.code" :label="`${airline.code} - ${getAirlineName(airline.code)}`" :value="airline.code"></el-option>
                        </el-select>
                        <el-select v-model="filterTicketType" placeholder="票证类型" clearable size="small" filterable>
                            <el-option label="全部" value=""></el-option>
                            <el-option label="所有" value="ALL"></el-option>
                            <el-option label="GP" value="GP"></el-option>
                            <el-option label="BSP" value="BSP"></el-option>
                            <el-option label="B2B" value="B2B"></el-option>
                        </el-select>
                        <el-select v-model="filterProductType" placeholder="产品类型" clearable size="small" filterable>
                            <el-option label="全部类型" value=""></el-option>
                            <el-option label="常规产品" value="常规产品"></el-option>
                            <el-option label="贵宾室服务" value="贵宾室服务"></el-option>
                            <el-option label="变更服务" value="变更服务"></el-option>
                            <el-option label="伴手礼服务" value="伴手礼服务"></el-option>
                        </el-select>
                        <el-select v-model="filterOffice" placeholder="Office号" clearable size="small" filterable>
                            <el-option label="全部Office" value=""></el-option>
                            <el-option v-for="office in officeList" :key="office" :label="office" :value="office"></el-option>
                        </el-select>
                        <el-input v-model="searchText" placeholder="搜索产品" prefix-icon="el-icon-search" style="width:180px" size="small" clearable></el-input>
                        <el-button type="success" icon="el-icon-document" size="small" @click="showViewHistory">查阅记录</el-button>
                    </div>
                </div>

                <div class="data-panel">
                    <el-table :data="filteredProducts" border style="width:100%" stripe :cell-style="{padding:'3px'}" :header-cell-style="{padding:'3px',background:'#f5f7fa',height:'32px'}" :row-style="{height:'32px'}" size="mini" @row-click="handleRowClick" style="cursor:pointer">
                        <el-table-column prop="product_name" label="产品名称" min-width="120">
                            <template slot-scope="scope">
                                {{scope.row.product_name}}
                                <span v-if="isNewProduct(scope.row)" class="tag-new">新</span>
                            </template>
                        </el-table-column>
                        <el-table-column prop="policy_code" label="政策代码" min-width="100" align="center">
                            <template slot-scope="scope">
                                <span class="tag-price">{{scope.row.policy_code || '-'}}</span>
                            </template>
                        </el-table-column>
                        <el-table-column prop="price_increase" label="价格" width="60" align="right">
                            <template slot-scope="scope">
                                ¥{{scope.row.price_increase || 0}}
                            </template>
                        </el-table-column>
                        <el-table-column prop="rebate_ratio" label="后返" width="70" align="center"></el-table-column>
                        <el-table-column prop="settlement" label="结算方式" width="90" align="center">
                            <template slot-scope="scope">
                                <span style="color:#e6a23c;font-size:11px">{{scope.row.settlement || '-'}}</span>
                            </template>
                        </el-table-column>
                        <el-table-column prop="route" label="航线" min-width="90"></el-table-column>
                        <el-table-column prop="booking_class" label="订座舱位" min-width="110"></el-table-column>
                        <el-table-column prop="remarks" label="备注" min-width="90"></el-table-column>
                        <el-table-column prop="office" label="Office" min-width="110"></el-table-column>
                        <el-table-column prop="valid_period" label="有效期" min-width="90"></el-table-column>
                    </el-table>
                    <el-empty v-if="filteredProducts.length===0" description="暂无数据"></el-empty>
                </div>
            </div>
        </div>

        <!-- 阅查记录弹窗 -->
        <el-dialog title="查阅记录" :visible.sync="historyDialogVisible" width="800px">
            <el-table :data="viewHistory" border size="small" max-height="400">
                <el-table-column prop="viewTime" label="查看时间" width="160"></el-table-column>
                <el-table-column prop="productCode" label="政策代码" width="100" align="center"></el-table-column>
                <el-table-column prop="productName" label="产品名称" min-width="150"></el-table-column>
                <el-table-column prop="airline" label="航司" width="80" align="center"></el-table-column>
                <el-table-column prop="route" label="航线" min-width="120"></el-table-column>
            </el-table>
            <div slot="footer" class="dialog-footer">
                <el-button @click="historyDialogVisible = false">关闭</el-button>
                <el-button type="danger" @click="clearHistory" size="small">清空记录</el-button>
            </div>
        </el-dialog>

        <!-- 新产品提醒弹窗 -->
        <el-dialog title="🆕 新产品提醒" :visible.sync="newProductDialogVisible" width="600px" :before-close="handleCloseNewProductDialog">
            <el-alert
                title="发现新产品！"
                type="success"
                :description="`今日有 ${newProductCount} 个新产品更新`"
                :closable="false"
                show-icon
                style="margin-bottom: 15px">
            </el-alert>
            <el-table :data="newProducts" border size="small" max-height="300">
                <el-table-column prop="airline" label="航司" width="60" align="center"></el-table-column>
                <el-table-column prop="product_name" label="产品名称" min-width="120"></el-table-column>
                <el-table-column prop="policy_code" label="政策代码" width="100" align="center"></el-table-column>
                <el-table-column prop="route" label="航线" min-width="100"></el-table-column>
            </el-table>
            <div slot="footer" class="dialog-footer">
                <el-button type="primary" @click="handleCloseNewProductDialog">我知道了</el-button>
            </div>
        </el-dialog>
    </div>

    <!-- Vue & Element UI -->
    <script src="https://unpkg.com/vue@2.6.14/dist/vue.js"></script>
    <script src="https://unpkg.com/element-ui/lib/index.js"></script>
    <script>
        const API_BASE = '';
        const AIRLINE_NAMES = {
            'CA': '中国国际航空', 'MU': '中国东方航空', 'CZ': '中国南方航空', 'HU': '海南航空',
            'FM': '上海航空', 'MF': '厦门航空', 'SC': '山东航空', 'ZH': '深圳航空',
            '3U': '四川航空', 'KY': '昆明航空', 'BK': '奥凯航空', 'CN': '大新华航空',
            'EU': '成都航空', 'G5': '华夏航空', 'GS': '天津航空', 'HO': '吉祥航空',
            'JD': '首都航空', 'JR': '幸福航空', 'KN': '中国联合航空', 'NS': '河北航空',
            'OQ': '重庆航空', 'QW': '青岛航空', 'RY': '江西航空', 'TV': '西藏航空',
            'UQ': '乌鲁木齐航空', 'PN': '西部航空', '8L': '祥鹏航空', '9H': '长安航空',
            'A6': '湖南航空', 'DR': '瑞丽航空', 'FU': '福州航空', 'GJ': '长龙航空',
            'GX': '北部湾航空', 'DZ': '东海航空', 'LT': '龙江航空', 'GY': '多彩贵州'
        };

        new Vue({
            el: '#app',
            data: {
                isLoggedIn: false,
                loginForm: { username: '', password: '' },
                loginLoading: false,
                loginError: '',
                allAirlines: [],
                selectedAirline: '',
                products: [],
                filterTicketType: '',
                filterProductType: '',
                filterOffice: '',
                searchText: '',
                officeList: ['KMG319', 'CTU152', 'SZX146', 'KMG279'],
                historyDialogVisible: false,
                viewHistory: [],
                newProductDialogVisible: false,
                newProducts: [],
                newProductCount: 0,
                viewedProducts: new Set(),
                lastLoginDate: null
            },
            computed: {
                filteredProducts() {
                    let list = this.products;
                    if (this.filterTicketType) {
                        list = list.filter(p => (p.ticket_type||'').toUpperCase() === this.filterTicketType);
                    }
                    if (this.filterProductType) {
                        list = list.filter(p => this.getProductType(p) === this.filterProductType);
                    }
                    if (this.filterOffice) {
                        list = list.filter(p => (p.office||'').includes(this.filterOffice));
                    }
                    if (this.searchText) {
                        const s = this.searchText.toLowerCase();
                        list = list.filter(p => 
                            (p.product_name||'').toLowerCase().includes(s) ||
                            (p.route||'').toLowerCase().includes(s) ||
                            (p.policy_code||'').toLowerCase().includes(s)
                        );
                    }
                    return list;
                }
            },
            watch: {
                selectedAirline() {
                    this.loadProducts();
                }
            },
            mounted() {
                this.checkAuth();
                this.loadViewHistory();
            },
            methods: {
                checkAuth() {
                    const urlParams = new URLSearchParams(window.location.search);
                    let token = urlParams.get('token');
                    if (token) {
                        localStorage.setItem('auth_token', token);
                        window.history.replaceState({}, document.title, '/');
                    } else {
                        token = localStorage.getItem('auth_token');
                    }
                    if (token) {
                        this.isLoggedIn = true;
                        this.loadAirlines();
                    }
                },
                getAuthHeader() {
                    const token = localStorage.getItem('auth_token');
                    return token ? { 'Authorization': `Bearer ${token}` } : {};
                },
                handleLogout() {
                    localStorage.removeItem('auth_token');
                    this.isLoggedIn = false;
                },
                async handleLogin() {
                    if (!this.loginForm.username || !this.loginForm.password) return;
                    this.loginLoading = true;
                    this.loginError = '';
                    try {
                        const resp = await fetch(`${API_BASE}/api/login`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(this.loginForm)
                        });
                        const data = await resp.json();
                        if (data.success) {
                            localStorage.setItem('auth_token', data.token);
                            this.isLoggedIn = true;
                            await this.loadAirlines();
                            await this.loadProducts();
                            this.checkNewProducts();
                        } else {
                            this.loginError = data.message || '账号或密码错误';
                        }
                    } catch (e) {
                        this.loginError = '网络错误';
                        console.error('Login error:', e);
                    } finally {
                        this.loginLoading = false;
                    }
                },
                getAirlineName(code) {
                    return AIRLINE_NAMES[code] || code;
                },
                async loadAirlines() {
                    try {
                        const resp = await fetch(`${API_BASE}/api/airlines`, { headers: this.getAuthHeader() });
                        const data = await resp.json();
                        if (data.success) this.allAirlines = data.data.airlines || [];
                    } catch (e) {
                        console.error('Failed to load airlines:', e);
                        this.allAirlines = [];
                    }
                },
                async loadProducts() {
                    try {
                        let url = `${API_BASE}/api/products`;
                        if (this.selectedAirline) {
                            url = `${API_BASE}/api/airlines/${this.selectedAirline}`;
                        }
                        console.log('Loading products from:', url);
                        const resp = await fetch(url);
                        const data = await resp.json();
                        console.log('Response:', data);
                        if (data.success) {
                            this.products = data.data.products || [];
                            console.log('Products loaded:', this.products.length);
                        }
                    } catch (e) {
                        console.error('Failed to load products:', e);
                        this.products = [];
                    }
                },
                getProductType(product) {
                    const name = (product.product_name||'').toLowerCase();
                    if (name.includes('贵宾室')) return '贵宾室服务';
                    if (name.includes('变更')||name.includes('改期')) return '变更服务';
                    if (name.includes('伴手礼')) return '伴手礼服务';
                    return '常规产品';
                },
                handleRowClick(row) {
                    this.recordView(row);
                },
                recordView(product) {
                    const record = {
                        viewTime: new Date().toLocaleString('zh-CN'),
                        productCode: product.policy_code || '-',
                        productName: product.product_name,
                        airline: product.airline,
                        route: product.route
                    };
                    this.viewHistory.unshift(record);
                    if (this.viewHistory.length > 100) {
                        this.viewHistory.pop();
                    }
                    this.viewedProducts.add(product.policy_code || product.product_name);
                    this.saveViewHistory();
                },
                loadViewHistory() {
                    const saved = localStorage.getItem('viewHistory');
                    const viewed = localStorage.getItem('viewedProducts');
                    const lastDate = localStorage.getItem('lastLoginDate');
                    if (saved) {
                        try {
                            this.viewHistory = JSON.parse(saved);
                        } catch (e) {
                            this.viewHistory = [];
                        }
                    }
                    if (viewed) {
                        try {
                            const arr = JSON.parse(viewed);
                            this.viewedProducts = new Set(arr);
                        } catch (e) {
                            this.viewedProducts = new Set();
                        }
                    }
                    if (lastDate) {
                        this.lastLoginDate = lastDate;
                    }
                },
                saveViewHistory() {
                    localStorage.setItem('viewHistory', JSON.stringify(this.viewHistory));
                    localStorage.setItem('viewedProducts', JSON.stringify(Array.from(this.viewedProducts)));
                },
                showViewHistory() {
                    this.historyDialogVisible = true;
                },
                clearHistory() {
                    this.$confirm('确定清空所有查阅记录吗？', '提示', {
                        confirmButtonText: '确定',
                        cancelButtonText: '取消',
                        type: 'warning'
                    }).then(() => {
                        this.viewHistory = [];
                        this.viewedProducts.clear();
                        this.saveViewHistory();
                        this.$message.success('查阅记录已清空');
                    }).catch(() => {});
                },
                checkNewProducts() {
                    const today = new Date().toLocaleDateString('zh-CN');
                    const lastDate = this.lastLoginDate;

                    if (lastDate && lastDate !== today) {
                        // 上次登录不是今天，检查新产品
                        this.newProducts = this.products.filter(p => !this.viewedProducts.has(p.policy_code || p.product_name)).slice(0, 20);
                        this.newProductCount = this.newProducts.length;

                        if (this.newProductCount > 0) {
                            this.newProductDialogVisible = true;
                        }
                    }

                    localStorage.setItem('lastLoginDate', today);
                },
                isNewProduct(product) {
                    const key = product.policy_code || product.product_name;
                    return !this.viewedProducts.has(key);
                },
                handleCloseNewProductDialog() {
                    this.newProductDialogVisible = false;
                    // 将新产品标记为已查看
                    this.newProducts.forEach(p => {
                        this.viewedProducts.add(p.policy_code || p.product_name);
                    });
                    this.saveViewHistory();
                }
            }
        });
    </script>
</body>
</html>
"""

@app.get("/")
@app.head("/")
async def index():
    """首页"""
    return HTMLResponse(content=HTML_TEMPLATE)

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
    limit: int = Query(100, description="返回数量限制")
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
