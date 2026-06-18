// 航空公司产品智能体 - 简洁版

const API_BASE = window.location.origin;
let allProducts = [];
let selectedAirline = '';
let selectedTicketType = '';

// 页面加载
document.addEventListener('DOMContentLoaded', function() {
    initApp();
});

// 初始化
async function initApp() {
    showLoading();
    try {
        console.log('开始初始化...');
        await loadAllProducts();
        console.log('产品加载完成，开始渲染...');
        initFilterTags();
        renderQuickAirlines();
        // 默认显示所有产品
        renderResults(allProducts);
        console.log('初始化完成');
    } catch (error) {
        console.error('初始化失败:', error);
        alert('加载失败，请刷新页面重试');
    } finally {
        hideLoading();
    }
}

// 加载所有产品
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

            console.log(`已加载 ${allProducts.length} 个产品`);
        }
    } catch (error) {
        console.error('加载产品失败:', error);
    }
}

// 初始化筛选标签
function initFilterTags() {
    // 票证类型标签
    document.querySelectorAll('#ticketTypeTags .filter-tag').forEach(tag => {
        tag.addEventListener('click', function() {
            document.querySelectorAll('#ticketTypeTags .filter-tag').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            selectedTicketType = this.dataset.type;
            applyFilters();
        });
    });
}

// 渲染快捷航司
function renderQuickAirlines() {
    const container = document.getElementById('quickAirlines');
    const topAirlines = ['CA', 'MU', 'CZ', 'HU', 'FM', 'MF', 'SC', 'ZH', '3U', 'KY'];

    container.innerHTML = topAirlines.map(code => {
        const name = getAirlineName(code);
        return `<span class="airline-badge" data-code="${code}" onclick="selectAirline('${code}')">${code} ${name}</span>`;
    }).join('');
}

// 选择航司
function selectAirline(code) {
    console.log('选择航司:', code);

    // 切换选中状态
    const badges = document.querySelectorAll('.airline-badge');
    badges.forEach(badge => {
        if (badge.dataset.code === code) {
            badge.classList.toggle('active');
            selectedAirline = badge.classList.contains('active') ? code : '';
        } else {
            badge.classList.remove('active');
        }
    });

    console.log('选中航司:', selectedAirline);

    // 立即应用筛选并显示结果
    if (selectedAirline) {
        // 如果选中了航司，直接筛选
        const results = allProducts.filter(p => p.airline === selectedAirline);
        renderResults(results);
    } else {
        // 取消选择，显示所有产品
        renderResults(allProducts);
    }
}

// 执行智能搜索
function performSearch() {
    const keyword = document.getElementById('searchInput').value.trim();
    console.log('执行搜索:', keyword);

    if (!keyword) {
        console.log('搜索关键词为空，显示所有产品');
        renderResults(allProducts);
        return;
    }

    applyFilters(keyword);
}

// 应用筛选和搜索
function applyFilters(keyword = null) {
    showLoading();

    // 获取搜索关键词
    if (keyword === null) {
        keyword = document.getElementById('searchInput').value.trim();
    }

    // 解析智能关键词
    const searchParams = parseSmartSearch(keyword);

    let results = allProducts;

    // 1. 应用航司筛选
    if (selectedAirline) {
        results = results.filter(p => p.airline === selectedAirline);
    }

    // 2. 应用票证类型筛选
    if (selectedTicketType) {
        results = results.filter(p => p.ticket_type === selectedTicketType);
    }

    // 3. 应用智能搜索
    if (searchParams.airlines.length > 0) {
        results = results.filter(p => searchParams.airlines.includes(p.airline));
    }

    if (searchParams.bookingClasses.length > 0) {
        results = results.filter(p => {
            return searchParams.bookingClasses.some(cls => 
                p.booking_class && p.booking_class.includes(cls)
            );
        });
    }

    if (searchParams.offices.length > 0) {
        results = results.filter(p => {
            return searchParams.offices.some(office => 
                p.office && p.office.includes(office)
            );
        });
    }

    if (searchParams.keywords.length > 0) {
        results = results.filter(p => {
            const searchableText = [
                p.product_name,
                p.route,
                p.booking_class,
                p.office,
                p.policy_identifier,
                p.remarks
            ].join(' ').toLowerCase();

            return searchParams.keywords.every(kw => 
                searchableText.includes(kw.toLowerCase())
            );
        });
    }

    // 4. 应用价格范围
    if (searchParams.minPrice !== null) {
        results = results.filter(p => {
            const price = parseFloat(p.price_increase) || 0;
            return price >= searchParams.minPrice;
        });
    }

    if (searchParams.maxPrice !== null) {
        results = results.filter(p => {
            const price = parseFloat(p.price_increase) || 0;
            return price <= searchParams.maxPrice;
        });
    }

    // 延迟渲染以显示加载动画
    setTimeout(() => {
        renderResults(results);
        hideLoading();
    }, 100);
}

// 智能解析搜索关键词
function parseSmartSearch(keyword) {
    const params = {
        airlines: [],
        bookingClasses: [],
        offices: [],
        keywords: [],
        minPrice: null,
        maxPrice: null
    };

    if (!keyword) return params;

    // 航司代码匹配（如：海南航空、HU、CA）
    const airlinePatterns = {
        '中国国际航空': 'CA', '国航': 'CA',
        '中国东方航空': 'MU', '东航': 'MU',
        '中国南方航空': 'CZ', '南航': 'CZ',
        '海南航空': 'HU', '海航': 'HU',
        '上海航空': 'FM', '上航': 'FM',
        '厦门航空': 'MF', '厦航': 'MF',
        '山东航空': 'SC', '山航': 'SC',
        '深圳航空': 'ZH', '深航': 'ZH',
        '四川航空': '3U', '川航': '3U',
        '昆明航空': 'KY', '昆航': 'KY'
    };

    // 匹配航司
    for (const [name, code] of Object.entries(airlinePatterns)) {
        if (keyword.includes(name) || keyword.toUpperCase().includes(code)) {
            params.airlines.push(code);
        }
    }

    // 舱位匹配（如：Q舱、Y舱、头等舱）
    const classPatterns = /([A-Z]\s*舱|头等舱|商务舱|经济舱)/g;
    const classMatches = keyword.match(classPatterns);
    if (classMatches) {
        classMatches.forEach(match => {
            params.bookingClasses.push(match.replace(/\s+/g, ''));
        });
    }

    // Office编号匹配（3-4个字母+3个数字）
    const officePattern = /([A-Z]{2,4}\d{3})/g;
    const officeMatches = keyword.match(officePattern);
    if (officeMatches) {
        params.offices = officeMatches;
    }

    // 价格范围匹配（如：100-200、100元以内、200元以上）
    const pricePattern = /(\d+)\s*[-~到]\s*(\d+)\s*元?/g;
    const priceMatch = pricePattern.exec(keyword);
    if (priceMatch) {
        params.minPrice = parseFloat(priceMatch[1]);
        params.maxPrice = parseFloat(priceMatch[2]);
    } else {
        // 单向价格
        const minPattern = /(\d+)\s*元以内|小于\s*(\d+)\s*元/i;
        const maxPattern = /(\d+)\s*元以上|大于\s*(\d+)\s*元/i;

        if (minPattern.test(keyword)) {
            const match = keyword.match(/(\d+)\s*元以内|小于\s*(\d+)\s*元/i);
            params.maxPrice = parseFloat(match[1]);
        } else if (maxPattern.test(keyword)) {
            const match = keyword.match(/(\d+)\s*元以上|大于\s*(\d+)\s*元/i);
            params.minPrice = parseFloat(match[1]);
        }
    }

    // 提取其他关键词
    let cleanKeyword = keyword;
    // 移除已识别的模式
    Object.keys(airlinePatterns).forEach(name => {
        cleanKeyword = cleanKeyword.replace(new RegExp(name, 'gi'), '');
    });
    cleanKeyword = cleanKeyword.replace(classPattern, '');
    cleanKeyword = cleanKeyword.replace(officePattern, '');
    cleanKeyword = cleanKeyword.replace(pricePattern, '');

    // 剩余的词作为关键词
    const remainingWords = cleanKeyword.split(/[\s,，]+/).filter(w => w.trim());
    params.keywords = remainingWords;

    return params;
}

// 渲染结果
function renderResults(products) {
    const container = document.getElementById('resultsList');
    const countEl = document.getElementById('resultsCount');

    countEl.textContent = products.length;

    if (products.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🔍</div>
                <p>没有找到匹配的产品</p>
                <p style="font-size: 12px; margin-top: 10px; color: #999;">尝试调整搜索词或筛选条件</p>
            </div>
        `;
        return;
    }

    container.innerHTML = products.map(product => renderProductCard(product)).join('');
}

// 渲染产品卡片（简洁版）
function renderProductCard(product) {
    const airlineName = getAirlineName(product.airline);
    const ticketTypeClass = product.ticket_type ? product.ticket_type.toLowerCase() : 'default';

    return `
        <div class="product-card" onclick="toggleDetails(this)">
            <div class="product-main">
                <div class="product-info">
                    <div class="product-name">${product.product_name || '未命名产品'}</div>
                    <div class="product-meta">
                        <div class="product-meta-item">
                            <span>✈️</span>
                            <span>${airlineName}</span>
                        </div>
                        <div class="product-meta-item">
                            <span>📋</span>
                            <span>${product.route || '-'}</span>
                        </div>
                        <div class="product-meta-item">
                            <span>💺</span>
                            <span>${product.booking_class?.substring(0, 20) || '-'}</span>
                        </div>
                    </div>
                </div>
                <div class="product-price">
                    <div class="price-label">溢价</div>
                    <div class="price-value">
                        ${product.price_increase || 0}
                        <span class="price-unit">元</span>
                    </div>
                    <div style="font-size: 12px; color: #999; margin-top: 2px;">
                        返点 ${product.rebate_ratio || '-'}
                    </div>
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

// 切换详情显示
function toggleDetails(card) {
    const details = card.querySelector('.product-details');
    details.classList.toggle('show');
}

// 清除所有筛选
function clearAll() {
    document.getElementById('searchInput').value = '';
    selectedAirline = '';
    selectedTicketType = '';

    document.querySelectorAll('.airline-badge').forEach(badge => badge.classList.remove('active'));
    document.querySelectorAll('#ticketTypeTags .filter-tag').forEach((tag, index) => {
        if (index === 0) {
            tag.classList.add('active');
        } else {
            tag.classList.remove('active');
        }
    });

    renderResults(allProducts);
}

// 航司名称映射
function getAirlineName(code) {
    const names = {
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
    return names[code] || code;
}

// 显示/隐藏加载
function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('resultsList').classList.add('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('resultsList').classList.remove('hidden');
}
