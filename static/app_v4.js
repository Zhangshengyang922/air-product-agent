// 航空公司产品智能体 - 航司分类版

const API_BASE = window.location.origin;
let allAirlines = [];
let allProducts = {};
let selectedAirline = '';
let selectedTicketType = '';

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

// 页面加载
document.addEventListener('DOMContentLoaded', function() {
    initApp();
});

// 初始化
async function initApp() {
    showLoading();
    try {
        console.log('开始加载航司列表...');
        await loadAirlines();
        console.log('航司列表加载完成');
        renderAirlines();
        initFilterTags();
        hideLoading();
    } catch (error) {
        console.error('初始化失败:', error);
        alert('加载失败，请刷新页面重试');
        hideLoading();
    }
}

// 加载航司列表
async function loadAirlines() {
    try {
        const response = await fetch(`${API_BASE}/api/airlines`);
        const data = await response.json();

        if (data.success && data.data.airlines) {
            allAirlines = data.data.airlines;
            console.log(`已加载 ${allAirlines.length} 个航司`);
        }
    } catch (error) {
        console.error('加载航司列表失败:', error);
        throw error;
    }
}

// 渲染航司列表
function renderAirlines(filter = '') {
    const container = document.getElementById('airlineList');

    if (!allAirlines || allAirlines.length === 0) {
        container.innerHTML = '<div style="text-align:center;color:#999;padding:20px;">暂无航司数据</div>';
        return;
    }

    // 过滤航司
    let filteredAirlines = allAirlines;
    if (filter) {
        const lowerFilter = filter.toLowerCase();
        filteredAirlines = allAirlines.filter(airline => {
            const name = AIRLINE_NAMES[airline.code] || airline.code;
            return airline.code.toLowerCase().includes(lowerFilter) ||
                   name.toLowerCase().includes(lowerFilter);
        });
    }

    container.innerHTML = filteredAirlines.map(airline => {
        const name = AIRLINE_NAMES[airline.code] || airline.code;
        // 获取该航司的产品数量（如果已加载）
        const count = allProducts[airline.code] ? allProducts[airline.code].length : 0;

        return `
            <div class="airline-item ${selectedAirline === airline.code ? 'active' : ''}" 
                 onclick="selectAirline('${airline.code}')"
                 data-code="${airline.code}">
                <div class="airline-item-main">
                    <span class="airline-code">${airline.code}</span>
                    <span class="airline-name">${name}</span>
                </div>
                <span class="airline-count">${count > 0 ? count : '•'}</span>
            </div>
        `;
    }).join('');
}

// 搜索航司
function filterAirlines() {
    const keyword = document.getElementById('airlineSearch').value.trim();
    renderAirlines(keyword);
}

// 选择航司
async function selectAirline(code) {
    console.log('选择航司:', code);

    // 如果是同一个航司，不重复加载
    if (selectedAirline === code) {
        console.log('航司已选中，直接显示缓存产品');
        const products = allProducts[code];
        if (products) {
            renderProducts(products);
            updateTitle(AIRLINE_NAMES[code] || code);
        }
        return;
    }

    // 更新UI状态
    document.querySelectorAll('.airline-item').forEach(item => {
        if (item.dataset.code === code) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    selectedAirline = code;

    // 加载航司产品
    showLoading();
    console.log('开始加载航司产品:', code);
    try {
        const response = await fetch(`${API_BASE}/api/airlines/${code}`);
        const data = await response.json();

        console.log('API响应:', data);

        if (data.success && data.data.products) {
            // 缓存产品数据
            allProducts[code] = data.data.products;

            // 更新航司列表中的数量显示
            renderAirlines(document.getElementById('airlineSearch').value);

            // 渲染产品
            renderProducts(data.data.products);
            updateTitle(AIRLINE_NAMES[code] || code);

            console.log(`已加载 ${data.data.count} 个${code}航司产品`);
        } else {
            console.error('API返回失败:', data);
            alert('加载产品失败：' + (data.message || '未知错误'));
        }
    } catch (error) {
        console.error('加载航司产品失败:', error);
        alert('加载产品失败，请重试');
    } finally {
        hideLoading();
    }
}

// 更新标题
function updateTitle(text) {
    const titleEl = document.getElementById('contentTitle');
    const countEl = document.getElementById('productsCount');

    titleEl.textContent = `${text} 产品`;
}

// 渲染产品列表
function renderProducts(products) {
    const container = document.getElementById('productsList');
    const countEl = document.getElementById('productsCount');

    // 应用票证类型筛选
    let filteredProducts = products;
    if (selectedTicketType) {
        filteredProducts = products.filter(p => p.ticket_type === selectedTicketType);
    }

    countEl.textContent = filteredProducts.length;

    if (filteredProducts.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📦</div>
                <p>暂无产品</p>
                ${selectedTicketType ? '<p style="font-size:12px;margin-top:10px;">尝试切换票证类型</p>' : ''}
            </div>
        `;
        return;
    }

    container.innerHTML = filteredProducts.map(product => renderProductCard(product)).join('');
}

// 渲染产品卡片
function renderProductCard(product) {
    const ticketTypeClass = product.ticket_type ? product.ticket_type.toLowerCase() : 'default';

    return `
        <div class="product-card" onclick="toggleDetails(this)">
            <div class="product-header">
                <div class="product-name">${product.product_name || '未命名产品'}</div>
                <div class="product-price">
                    <div class="price-value">${product.price_increase || 0}</div>
                    <div class="price-unit">元</div>
                </div>
            </div>

            <div class="product-info">
                <div class="product-info-item">
                    <span>📋</span>
                    <span>${product.route || '-'}</span>
                </div>
                <div class="product-info-item">
                    <span>💺</span>
                    <span>${product.booking_class?.substring(0, 20) || '-'}</span>
                </div>
                <div class="product-info-item">
                    <span>💰</span>
                    <span>返点 ${product.rebate_ratio || '-'}</span>
                </div>
            </div>

            <div class="product-details">
                <div class="detail-row">
                    <div class="detail-item">
                        <span class="detail-label">Office:</span>
                        <span class="detail-value">${product.office || '-'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">有效期:</span>
                        <span class="detail-value">${product.valid_period || '-'}</span>
                    </div>
                </div>
                <div class="detail-row">
                    <div class="detail-item">
                        <span class="detail-label">舱位:</span>
                        <span class="detail-value">${product.booking_class || '-'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">标识:</span>
                        <span class="detail-value">${product.policy_identifier || '-'}</span>
                    </div>
                </div>
                ${product.remarks ? `
                    <div class="detail-row">
                        <div class="detail-item">
                            <span class="detail-label">备注:</span>
                            <span class="detail-value" style="color: #666;">${product.remarks}</span>
                        </div>
                    </div>
                ` : ''}
                <div class="product-tags">
                    <span class="tag ${ticketTypeClass}">${product.ticket_type || 'ALL'}</span>
                    ${product.policy_identifier ? `<span class="tag default">${product.policy_identifier}</span>` : ''}
                </div>
            </div>
        </div>
    `;
}

// 初始化筛选标签
function initFilterTags() {
    document.querySelectorAll('#quickFilters .filter-chip').forEach(chip => {
        chip.addEventListener('click', function() {
            document.querySelectorAll('#quickFilters .filter-chip').forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            selectedTicketType = this.dataset.type;

            // 如果已选择航司，重新筛选
            if (selectedAirline && allProducts[selectedAirline]) {
                renderProducts(allProducts[selectedAirline]);
            }
        });
    });
}

// 切换详情显示
function toggleDetails(card) {
    const details = card.querySelector('.product-details');
    details.classList.toggle('show');
}

// 显示/隐藏加载
function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('productsList').classList.add('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('productsList').classList.remove('hidden');
}
