// API配置 - 使用相对路径，支持局域网访问
const API_BASE = '';

// 航司名称映射
const AIRLINE_NAMES = {
    'CA': '中国国际航空',
    'MU': '中国东方航空',
    'CZ': '中国南方航空',
    'HU': '海南航空',
    'FM': '上海航空',
    'MF': '厦门航空',
    'SC': '山东航空',
    'ZH': '深圳航空',
    '3U': '四川航空',
    'KY': '昆明航空',
    'BK': '昆明航空',
    'CN': '大新华航空',
    'EU': '成都航空',
    'G5': '华夏航空',
    'GS': '天津航空',
    'HO': '吉祥航空',
    'JD': '首都航空',
    'JR': '幸福航空',
    'KN': '中国联合航空',
    'NS': '河北航空',
    'OQ': '重庆航空',
    'QW': '青岛航空',
    'RY': '江西航空',
    'TV': '西藏航空',
    'UQ': '乌鲁木齐航空',
    'VQ': '西部航空',
    'YI': '福州航空',
    'ZG': '桂林航空'
};

// 全局状态
let allAirlines = [];
let currentProducts = [];
let selectedAirline = '';
let selectedTicketType = '';

// 显示/隐藏加载状态
function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

// 初始化
async function initApp() {
    console.log('🚀 初始化应用...');
    showLoading();
    
    try {
        // 加载航司列表
        await loadAirlines();
        console.log('✅ 应用初始化完成');
    } catch (error) {
        console.error('❌ 初始化失败:', error);
        alert('加载失败，请刷新页面重试');
    } finally {
        hideLoading();
    }
}

// 加载航司列表
async function loadAirlines() {
    console.log('📡 加载航司列表...');
    
    try {
        const response = await fetch(`${API_BASE}/api/airlines`);
        const data = await response.json();

        console.log('📊 航司列表响应:', data);

        if (data.success && data.data.airlines) {
            allAirlines = data.data.airlines;
            renderAirlines();
            console.log(`✅ 已加载 ${allAirlines.length} 个航司`);
        } else {
            throw new Error('加载航司列表失败');
        }
    } catch (error) {
        console.error('❌ 加载航司列表失败:', error);
        throw error;
    }
}

// 渲染航司列表
function renderAirlines(filter = '') {
    console.log('🎨 渲染航司列表, 过滤词:', filter);
    
    const container = document.getElementById('airlineList');
    
    // 过滤航司
    let airlines = allAirlines;
    if (filter) {
        const lowerFilter = filter.toLowerCase();
        airlines = allAirlines.filter(airline => 
            airline.code.toLowerCase().includes(lowerFilter) ||
            airline.name.toLowerCase().includes(lowerFilter)
        );
    }

    if (airlines.length === 0) {
        container.innerHTML = `
            <div class="no-results">
                <div style="font-size: 32px; margin-bottom: 10px;">🔍</div>
                <p>未找到匹配的航司</p>
            </div>
        `;
        return;
    }

    // 渲染航司列表
    container.innerHTML = airlines.map(airline => {
        const name = AIRLINE_NAMES[airline.code] || airline.name || airline.code;
        const count = airline.product_count || 0;
        
        return `
            <div class="airline-item" 
                 data-code="${airline.code}" 
                 onclick="selectAirline('${airline.code}')">
                <div class="airline-item-main">
                    <span class="airline-code">${airline.code}</span>
                    <span class="airline-name">${name}</span>
                </div>
                <span class="airline-count">${count}</span>
            </div>
        `;
    }).join('');

    // 恢复选中状态
    if (selectedAirline) {
        const selectedItem = container.querySelector(`[data-code="${selectedAirline}"]`);
        if (selectedItem) {
            selectedItem.classList.add('active');
        }
    }

    console.log(`✅ 已渲染 ${airlines.length} 个航司`);
}

// 筛选航司
function filterAirlines() {
    const filter = document.getElementById('airlineSearch').value.trim();
    renderAirlines(filter);
}

// 选择航司
async function selectAirline(code) {
    console.log('✈️ 选择航司:', code);
    
    // 如果是同一个航司，不重复加载
    if (selectedAirline === code) {
        console.log('航司已选中，直接显示产品');
        const filteredProducts = filterProducts(currentProducts);
        renderProducts(filteredProducts);
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
    console.log('📡 加载航司产品:', code);
    
    try {
        const response = await fetch(`${API_BASE}/api/airlines/${code}`);
        const data = await response.json();

        console.log('📊 API响应:', data);

        if (data.success && data.data.products) {
            currentProducts = data.data.products;
            
            // 更新标题
            const name = AIRLINE_NAMES[code] || code;
            updateTitle(name + ' 产品');
            
            // 应用筛选并渲染
            const filteredProducts = filterProducts(currentProducts);
            renderProducts(filteredProducts);

            console.log(`✅ 已加载 ${data.data.count} 个${code}航司产品`);
        } else {
            throw new Error(data.message || '加载产品失败');
        }
    } catch (error) {
        console.error('❌ 加载航司产品失败:', error);
        alert('加载产品失败: ' + error.message);
    } finally {
        hideLoading();
    }
}

// 筛选产品
function filterProducts(products) {
    console.log('🔍 筛选产品, 票证类型:', selectedTicketType);
    
    let filtered = [...products];
    
    // 按票证类型筛选
    if (selectedTicketType) {
        filtered = filtered.filter(p => {
            if (!p.ticket_type) return false;
            return p.ticket_type.toUpperCase() === selectedTicketType;
        });
    }

    console.log(`✅ 筛选后剩余 ${filtered.length} 个产品`);
    return filtered;
}

// 渲染产品列表
function renderProducts(products) {
    console.log('🎨 渲染产品列表, 产品数量:', products.length);
    
    const container = document.getElementById('productsList');
    const countSpan = document.getElementById('productsCount');
    
    // 更新数量
    countSpan.textContent = products.length;

    if (!products || products.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📦</div>
                <p>暂无产品数据</p>
                <small>尝试调整筛选条件</small>
            </div>
        `;
        return;
    }

    // 渲染产品卡片
    container.innerHTML = products.map(product => renderProductCard(product)).join('');
    
    console.log('✅ 产品列表渲染完成');
}

// 渲染单个产品卡片
function renderProductCard(product) {
    const price = product.price_increase || 0;
    const rebate = product.rebate_ratio || '0';
    const ticketType = product.ticket_type || 'ALL';
    const ticketTypeClass = ticketType.toLowerCase();
    
    return `
        <div class="product-card" onclick="toggleProductDetails(this)">
            <div class="product-header">
                <div class="product-name">${product.product_name || '未命名产品'}</div>
                <div class="product-price">¥${price}</div>
            </div>

            ${product.office_id ? `
                <div class="product-office">Office: ${product.office_id}</div>
            ` : ''}

            <div class="product-basic-info">
                <div class="info-item">
                    <div class="info-label">航线</div>
                    <div class="info-value">${product.route || '-'}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">舱位</div>
                    <div class="info-value">${product.booking_class || '-'}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">返点</div>
                    <div class="info-value">${rebate}%</div>
                </div>
            </div>

            <div class="product-details">
                <div class="detail-row">
                    <span class="detail-label">航空公司:</span>
                    <span class="detail-value">${product.airline || '-'}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">舱位详情:</span>
                    <span class="detail-value">${product.cabin_class || '-'}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">有效期:</span>
                    <span class="detail-value">${product.valid_from || '-'} 至 ${product.valid_until || '-'}</span>
                </div>
                ${product.policy_identifier ? `
                    <div class="detail-row">
                        <span class="detail-label">产品标识:</span>
                        <span class="detail-value">${product.policy_identifier}</span>
                    </div>
                ` : ''}

                <div class="product-tags">
                    <span class="tag ${ticketTypeClass}">${ticketType}</span>
                    ${product.ticket_type_text ? `<span class="tag ${ticketTypeClass}">${product.ticket_type_text}</span>` : ''}
                </div>

                ${product.remarks ? `
                    <div class="product-remarks">
                        <strong>备注：</strong>${product.remarks}
                    </div>
                ` : ''}
            </div>
        </div>
    `;
}

// 切换产品详情
function toggleProductDetails(card) {
    card.classList.toggle('expanded');
    const details = card.querySelector('.product-details');
    details.classList.toggle('show');
}

// 更新标题
function updateTitle(title) {
    document.getElementById('contentTitle').textContent = title;
}

// 初始化票证类型筛选
function initFilterTags() {
    const chips = document.querySelectorAll('.filter-chip');
    
    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            const type = chip.dataset.type;
            
            // 更新选中状态
            chips.forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            
            // 更新筛选条件
            selectedTicketType = type;
            console.log('选择票证类型:', type || '全部');
            
            // 重新筛选并渲染
            if (currentProducts.length > 0) {
                const filtered = filterProducts(currentProducts);
                renderProducts(filtered);
            }
        });
    });

    console.log('✅ 票证类型筛选初始化完成');
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('📄 页面加载完成');
    initApp();
    initFilterTags();
});
