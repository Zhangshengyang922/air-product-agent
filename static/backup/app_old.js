// 航空公司产品智能体 - 前端JavaScript

// API基础URL
const API_BASE = window.location.origin;

// 全局状态
let currentPage = 1;
let currentAirline = null;
let currentTab = 'airlines';

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initApp();
});

// 初始化应用
async function initApp() {
    showLoading();
    try {
        await Promise.all([
            loadStats(),
            loadTicketTypes(),
            loadAirlines()
        ]);
    } catch (error) {
        showError('初始化失败: ' + error.message);
    } finally {
        hideLoading();
    }
}

// 加载统计信息
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/api/stats`);
        const data = await response.json();

        if (data.success) {
            document.getElementById('totalProducts').textContent = data.data.total_products || 0;
            document.getElementById('totalAirlines').textContent = data.data.total_airlines || 0;
            document.getElementById('totalRoutes').textContent = data.data.total_routes || 0;
        }
    } catch (error) {
        console.error('加载统计信息失败:', error);
    }
}

// 加载票证类型统计
async function loadTicketTypes() {
    try {
        const response = await fetch(`${API_BASE}/api/ticket-types`);
        const data = await response.json();

        if (data.success) {
            document.getElementById('gpCount').textContent = data.data.GP || 0;
            document.getElementById('bspCount').textContent = data.data.BSP || 0;
            document.getElementById('b2bCount').textContent = data.data.B2B || 0;
        }
    } catch (error) {
        console.error('加载票证类型统计失败:', error);
    }
}

// 加载航空公司列表
async function loadAirlines() {
    console.log('[DEBUG] 开始加载航司列表');
    try {
        const response = await fetch(`${API_BASE}/api/airlines`);
        console.log('[DEBUG] 航司列表响应状态:', response.status);
        const data = await response.json();
        console.log('[DEBUG] 航司列表数据:', data);

        if (data.success) {
            console.log('[DEBUG] 航司数量:', data.data.airlines.length);
            renderAirlines(data.data.airlines);
        }
    } catch (error) {
        console.error('[ERROR] 加载航空公司列表失败:', error);
        showError('加载航空公司列表失败');
    }
}

// 渲染航空公司列表
function renderAirlines(airlines) {
    const container = document.getElementById('airlinesList');
    
    if (!airlines || airlines.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🏢</div>
                <div class="empty-state-text">暂无航空公司数据</div>
            </div>
        `;
        return;
    }

    container.innerHTML = airlines.map(airline => `
        <div class="airline-card" onclick="loadAirlineProducts('${airline.code}')">
            <div class="airline-code">${airline.code}</div>
            <div class="airline-name">${airline.name || airline.code}</div>
        </div>
    `).join('');
}

// 加载航空公司产品
async function loadAirlineProducts(airlineCode) {
    console.log('[DEBUG] 开始加载航司产品:', airlineCode);
    showLoading();
    currentAirline = airlineCode;

    try {
        const url = `${API_BASE}/api/airlines/${airlineCode}`;
        console.log('[DEBUG] 请求URL:', url);
        
        const response = await fetch(url);
        console.log('[DEBUG] 响应状态:', response.status);
        
        const data = await response.json();
        console.log('[DEBUG] 响应数据:', data);

        if (data.success) {
            console.log('[DEBUG] 产品数量:', data.data.products.length);
            console.log('[DEBUG] 第一个产品:', data.data.products[0]);
            renderProducts(data.data.products, 'productsList');
            switchTab('products');
            
            // 更新标签页标题
            const tabBtn = document.querySelector('.tab-btn:nth-child(2)');
            if (tabBtn) {
                tabBtn.textContent = `📦 ${airlineCode} 产品 (${data.data.count})`;
            }
        } else {
            console.error('[ERROR] API返回失败:', data.message);
            showError(data.message || '加载产品失败');
        }
    } catch (error) {
        console.error('[ERROR] 加载产品异常:', error);
        showError('加载产品失败: ' + error.message);
    } finally {
        hideLoading();
    }
}

// 渲染产品列表
function renderProducts(products, containerId) {
    console.log('[DEBUG] 渲染产品列表, 容器ID:', containerId, '产品数量:', products?.length);
    
    const container = document.getElementById(containerId);
    
    if (!container) {
        console.error('[ERROR] 找不到容器:', containerId);
        return;
    }

    if (!products || products.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📦</div>
                <div class="empty-state-text">暂无产品数据</div>
            </div>
        `;
        return;
    }

    console.log('[DEBUG] 渲染第一个产品:', products[0]);

    container.innerHTML = products.map(product => `
        <div class="product-item">
            <div class="product-header">
                <div class="product-name">${product.product_name || '未命名产品'}</div>
                <div class="product-airline">${product.airline}</div>
            </div>
            <div class="product-details">
                <div class="product-detail">
                    <span class="detail-label">航线</span>
                    <span class="detail-value">${product.route || '-'}</span>
                </div>
                <div class="product-detail">
                    <span class="detail-label">舱位</span>
                    <span class="detail-value">${product.booking_class || '-'}</span>
                </div>
                <div class="product-detail">
                    <span class="detail-label">溢价</span>
                    <span class="detail-value">${product.price_increase || 0}元</span>
                </div>
                <div class="product-detail">
                    <span class="detail-label">返点</span>
                    <span class="detail-value">${product.rebate_ratio || '-'}</span>
                </div>
            </div>
            <div class="product-tags">
                ${product.ticket_type ? `<span class="tag ${product.ticket_type.toLowerCase()}">${product.ticket_type}</span>` : ''}
                ${product.policy_identifier ? `<span class="tag">${product.policy_identifier}</span>` : ''}
            </div>
            ${product.remarks ? `
                <div class="product-detail" style="margin-top: 10px;">
                    <span class="detail-label">备注</span>
                    <span class="detail-value">${product.remarks}</span>
                </div>
            ` : ''}
        </div>
    `).join('');
    
    console.log('[DEBUG] 产品列表渲染完成');
}

// 搜索产品
async function searchProducts() {
    const keyword = document.getElementById('searchInput').value.trim();

    if (!keyword) {
        showError('请输入搜索关键词');
        return;
    }

    showLoading();

    try {
        const response = await fetch(`${API_BASE}/api/search?keyword=${encodeURIComponent(keyword)}`);
        const data = await response.json();

        if (data.success) {
            renderProducts(data.data.products, 'searchResults');
            switchTab('search');
            
            // 更新标签页标题
            document.querySelector('.tab-btn:nth-child(3)').textContent = 
                `🔍 搜索结果 (${data.data.count})`;
        }
    } catch (error) {
        console.error('搜索失败:', error);
        showError('搜索失败');
    } finally {
        hideLoading();
    }
}

// 切换标签页
function switchTab(tabName) {
    currentTab = tabName;

    // 更新按钮状态
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target?.classList?.add('active');

    // 如果是函数调用，找到对应的按钮
    if (!event.target) {
        const tabMap = {
            'airlines': 0,
            'products': 1,
            'search': 2
        };
        document.querySelectorAll('.tab-btn')[tabMap[tabName]].classList.add('active');
    }

    // 切换内容
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}Tab`).classList.add('active');
}

// 筛选产品
async function filterProducts() {
    const ticketType = document.getElementById('ticketTypeFilter').value;

    if (!currentAirline) {
        showError('请先选择航空公司');
        return;
    }

    showLoading();

    try {
        let url = `${API_BASE}/api/airlines/${currentAirline}`;
        
        const response = await fetch(url);
        const data = await response.json();

        if (data.success) {
            // 在前端筛选票证类型
            let filteredProducts = data.data.products;
            if (ticketType !== 'ALL') {
                filteredProducts = filteredProducts.filter(p => 
                    p.ticket_type === ticketType || p.ticket_type === 'ALL'
                );
            }
            
            renderProducts(filteredProducts, 'productsList');
        }
    } catch (error) {
        console.error('筛选失败:', error);
        showError('筛选失败');
    } finally {
        hideLoading();
    }
}

// 显示加载动画
function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

// 隐藏加载动画
function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

// 显示错误信息
function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');

    setTimeout(() => {
        errorDiv.classList.add('hidden');
    }, 5000);
}

// 搜索框回车事件
document.getElementById('searchInput')?.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        searchProducts();
    }
});

// 刷新数据
async function refreshData() {
    await initApp();
}
