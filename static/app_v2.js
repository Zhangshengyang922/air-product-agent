// 航空公司产品智能体 - 优化版JavaScript

const API_BASE = window.location.origin;
let allProducts = []; // 缓存所有产品
let currentFilteredProducts = [];

// 页面加载
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
            loadAirlines(),
            loadAllProducts() // 预加载所有产品以便高级搜索
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
        }
    } catch (error) {
        console.error('加载统计信息失败:', error);
    }
}

// 加载票证类型
async function loadTicketTypes() {
    try {
        const response = await fetch(`${API_BASE}/api/ticket-types`);
        const data = await response.json();

        if (data.success) {
            document.getElementById('gpCount').textContent = data.data.GP || 0;
            document.getElementById('bspCount').textContent = data.data.BSP || 0;
        }
    } catch (error) {
        console.error('加载票证类型统计失败:', error);
    }
}

// 加载航司列表
async function loadAirlines() {
    try {
        const response = await fetch(`${API_BASE}/api/airlines`);
        const data = await response.json();

        if (data.success) {
            renderAirlines(data.data.airlines);
        }
    } catch (error) {
        console.error('加载航空公司列表失败:', error);
    }
}

// 渲染航司列表
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

// 加载航司产品
async function loadAirlineProducts(airlineCode) {
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/api/airlines/${airlineCode}`);
        const data = await response.json();

        if (data.success) {
            renderProducts(data.data.products, 'productsList');
            switchTab('products');

            const tabBtn = document.querySelector('.tab-btn:nth-child(2)');
            if (tabBtn) {
                tabBtn.textContent = `📦 ${airlineCode} 产品 (${data.data.count})`;
            }
        }
    } catch (error) {
        console.error('加载产品失败:', error);
        showError('加载产品失败');
    } finally {
        hideLoading();
    }
}

// 预加载所有产品（用于高级搜索）
async function loadAllProducts() {
    try {
        const response = await fetch(`${API_BASE}/api/airlines`);
        const data = await response.json();

        if (data.success && data.data.airlines) {
            allProducts = [];
            const airlines = data.data.airlines;

            for (const airline of airlines) {
                try {
                    const productResponse = await fetch(`${API_BASE}/api/airlines/${airline.code}`);
                    const productData = await productResponse.json();

                    if (productData.success && productData.data.products) {
                        allProducts = allProducts.concat(productData.data.products);
                    }
                } catch (error) {
                    console.error(`加载航司 ${airline.code} 产品失败:`, error);
                }
            }

            console.log(`已加载 ${allProducts.length} 个产品到内存`);
        }
    } catch (error) {
        console.error('预加载产品失败:', error);
    }
}

// 渲染产品列表（优化版）
function renderProducts(products, containerId) {
    const container = document.getElementById(containerId);

    if (!container) {
        console.error('找不到容器:', containerId);
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

    container.innerHTML = products.map(product => renderProductCard(product)).join('');
}

// 渲染单个产品卡片
function renderProductCard(product) {
    const airlineName = getAirlineName(product.airline);
    const ticketTypeClass = product.ticket_type ? product.ticket_type.toLowerCase() : 'default';

    return `
        <div class="product-card">
            <div class="product-header">
                <div class="product-name">${product.product_name || '未命名产品'}</div>
                <div class="product-badge">${airlineName}</div>
            </div>

            <div class="product-details-grid">
                <div class="product-detail-item">
                    <div class="detail-label">航线</div>
                    <div class="detail-value">${product.route || '-'}</div>
                </div>
                <div class="product-detail-item">
                    <div class="detail-label">舱位</div>
                    <div class="detail-value">${product.booking_class || '-'}</div>
                </div>
                <div class="product-detail-item">
                    <div class="detail-label">Office编号</div>
                    <div class="detail-value highlight">${product.office || '-'}</div>
                </div>
                <div class="product-detail-item">
                    <div class="detail-label">产品标识</div>
                    <div class="detail-value">${product.policy_identifier || '-'}</div>
                </div>
            </div>

            <div class="price-section">
                <div class="price-item">
                    <div class="price-label">溢价</div>
                    <div class="price-value">${product.price_increase || 0}元</div>
                </div>
                <div class="price-item">
                    <div class="price-label">返点</div>
                    <div class="price-value">${product.rebate_ratio || '-'}</div>
                </div>
            </div>

            <div class="valid-period">
                ${product.valid_period || '有效期未知'}
            </div>

            <div class="tags-container">
                <span class="tag ${ticketTypeClass}">${product.ticket_type || 'ALL'}</span>
                ${product.policy_identifier ? `<span class="tag default">${product.policy_identifier}</span>` : ''}
            </div>

            ${product.remarks ? `
                <div class="remarks-section">
                    <strong>备注：</strong>${product.remarks}
                </div>
            ` : ''}
        </div>
    `;
}

// 航司名称映射
const AIRLINE_NAMES = {
    'CA': '中国国际航空', 'MU': '中国东方航空', 'CZ': '中国南方航空',
    'HU': '海南航空', 'FM': '上海航空', 'MF': '厦门航空',
    'SC': '山东航空', 'ZH': '深圳航空', '3U': '四川航空',
    'KY': '昆明航空', '8L': '祥鹏航空', 'EU': '成都航空',
    'KN': '联合航空', 'OQ': '重庆航空', 'HO': '吉祥航空',
    'JD': '首都航空', 'TV': '西藏航空', 'DZ': '东海航空',
    'GT': '贵州航空', 'QW': '青岛航空', 'GJ': '长龙航空',
    'CN': '大新华航空', 'NS': '河北航空', 'DR': '瑞丽航空',
    'A6': '红土航空', 'UQ': '乌鲁木齐航空', 'PN': '西部航空'
};

function getAirlineName(code) {
    return AIRLINE_NAMES[code] || code;
}

// 执行搜索
async function performSearch() {
    const keyword = document.getElementById('searchInput').value.trim();

    if (!keyword) {
        showError('请输入搜索关键词');
        return;
    }

    showLoading();

    try {
        // 优先使用本地缓存进行搜索（更快）
        if (allProducts.length > 0) {
            const results = searchInCache(keyword);
            renderProducts(results, 'searchResults');
            switchTab('search');

            const tabBtn = document.querySelector('.tab-btn:nth-child(3)');
            if (tabBtn) {
                tabBtn.textContent = `🔍 搜索结果 (${results.length})`;
            }
        } else {
            // 如果缓存未加载，使用API搜索
            const response = await fetch(`${API_BASE}/api/search?keyword=${encodeURIComponent(keyword)}`);
            const data = await response.json();

            if (data.success) {
                renderProducts(data.data.products, 'searchResults');
                switchTab('search');

                const tabBtn = document.querySelector('.tab-btn:nth-child(3)');
                if (tabBtn) {
                    tabBtn.textContent = `🔍 搜索结果 (${data.data.count})`;
                }
            }
        }
    } catch (error) {
        console.error('搜索失败:', error);
        showError('搜索失败');
    } finally {
        hideLoading();
    }
}

// 在本地缓存中搜索
function searchInCache(keyword) {
    const lowerKeyword = keyword.toLowerCase();

    return allProducts.filter(product => {
        const searchableFields = [
            product.product_name,
            product.route,
            product.booking_class,
            product.office,
            product.airline,
            product.policy_identifier,
            product.remarks
        ].join(' ').toLowerCase();

        return searchableFields.includes(lowerKeyword);
    });
}

// 应用高级筛选
async function applyFilters() {
    if (currentTab !== 'search') {
        // 如果不在搜索标签页，先获取所有产品
        currentFilteredProducts = [...allProducts];
    }

    const ticketType = document.getElementById('ticketTypeFilter').value;
    const minPrice = parseFloat(document.getElementById('minPrice').value) || 0;
    const maxPrice = parseFloat(document.getElementById('maxPrice').value) || Infinity;

    showLoading();

    // 延迟执行以显示加载动画
    setTimeout(() => {
        let filtered = allProducts;

        // 筛选票证类型
        if (ticketType) {
            filtered = filtered.filter(p => p.ticket_type === ticketType);
        }

        // 筛选价格范围
        filtered = filtered.filter(p => {
            const price = parseFloat(p.price_increase) || 0;
            return price >= minPrice && price <= maxPrice;
        });

        currentFilteredProducts = filtered;
        renderProducts(filtered, 'searchResults');
        switchTab('search');

        const tabBtn = document.querySelector('.tab-btn:nth-child(3)');
        if (tabBtn) {
            tabBtn.textContent = `🔍 筛选结果 (${filtered.length})`;
        }

        hideLoading();
    }, 100);
}

// 重置筛选
function resetFilters() {
    document.getElementById('ticketTypeFilter').value = '';
    document.getElementById('minPrice').value = '';
    document.getElementById('maxPrice').value = '';
    document.getElementById('searchInput').value = '';

    switchTab('airlines');
}

// 标签页切换
let currentTab = 'airlines';

function switchTab(tabName) {
    currentTab = tabName;

    // 隐藏所有标签页
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // 移除所有按钮的active类
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // 显示选中的标签页
    document.getElementById(`${tabName}Tab`).classList.add('active');

    // 激活对应的按钮
    const buttonIndex = {
        'airlines': 0,
        'products': 1,
        'search': 2
    };
    document.querySelectorAll('.tab-btn')[buttonIndex[tabName]].classList.add('active');
}

// 显示加载中
function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('error').classList.add('hidden');
}

// 隐藏加载中
function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

// 显示错误
function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
    document.getElementById('loading').classList.add('hidden');
}
