(function () {
    'use strict';

    var isRu = (document.documentElement.lang || '').toLowerCase().indexOf('ru') === 0
        || /\/ru\//.test(location.pathname);

    var STATUS_CYCLE = ['paid', 'pending', 'shipped'];
    var STATUS_META = {
        paid: { label: 'Оплачено', className: 'pl-shop__status--paid' },
        pending: { label: 'В обробці', className: 'pl-shop__status--pending' },
        shipped: { label: 'Відправлено', className: 'pl-shop__status--shipped' }
    };

    var TITLE_MAP = {
        orders: 'Адмін / Замовлення',
        products: 'Адмін / Товари',
        analytics: 'Адмін / Аналітика'
    };

    var state = {
        orders: [
            {
                id: '10428',
                customer: 'Олена К.',
                sum: '₴1 290',
                status: 'paid',
                phone: '+380 67 123 45 67',
                email: 'olena.k@email.com',
                items: [
                    { name: 'Кросівки Nike Air', qty: 1, price: '₴990' },
                    { name: 'Шкарпетки бавовняні', qty: 2, price: '₴150' }
                ]
            },
            {
                id: '10427',
                customer: 'Андрій М.',
                sum: '₴3 099',
                status: 'pending',
                phone: '+380 50 987 65 43',
                email: 'andriy.m@email.com',
                items: [
                    { name: 'Куртка зимова', qty: 1, price: '₴2 509' },
                    { name: 'Шарф', qty: 1, price: '₴590' }
                ]
            },
            {
                id: '10426',
                customer: 'Ірина В.',
                sum: '₴1 999',
                status: 'shipped',
                phone: '+380 93 456 78 90',
                email: 'iryna.v@email.com',
                items: [
                    { name: 'Сумка шкіряна', qty: 1, price: '₴1 999' }
                ]
            },
            {
                id: '10425',
                customer: 'Максим Е.',
                sum: '₴2 489',
                status: 'paid',
                phone: '+380 66 234 56 78',
                email: 'max.t@email.com',
                items: [
                    { name: 'Годинник Casio', qty: 1, price: '₴2 489' }
                ]
            },
            {
                id: '10424',
                customer: 'Софія Л.',
                sum: '₴690',
                status: 'pending',
                phone: '+380 97 345 67 89',
                email: 'sofia.l@email.com',
                items: [
                    { name: 'Футболка oversize', qty: 2, price: '₴345' }
                ]
            }
        ],
        products: [
            {
                sku: 'NK-001',
                name: 'Кросівки Nike Air',
                price: '₴990',
                stock: 42,
                category: 'Взуття',
                visibility: 'active',
                visibilityLabel: 'Активний',
                sales30: 128,
                desc: 'Бестселер категорії. Синхронізація з Prom і Rozetka без ручного оновлення.'
            },
            {
                sku: 'JK-204',
                name: 'Куртка зимова',
                price: '₴2 890',
                stock: 8,
                category: 'Одяг',
                visibility: 'active',
                visibilityLabel: 'Активний',
                sales30: 54,
                desc: 'Преміум-позиція з високим середнім чеком. Залишки оновлюються після кожного замовлення.'
            },
            {
                sku: 'BG-118',
                name: 'Сумка шкіряна',
                price: '₴890',
                stock: 15,
                category: 'Аксесуари',
                visibility: 'active',
                visibilityLabel: 'Активний',
                sales30: 41,
                desc: 'Стабільні продажі з органічного трафіку. SEO-картка оптимізована під Google Shopping.'
            },
            {
                sku: 'CS-440',
                name: 'Годинник Casio',
                price: '₴2 150',
                stock: 3,
                category: 'Аксесуари',
                visibility: 'low',
                visibilityLabel: 'Мало на складі',
                sales30: 22,
                desc: 'Залишок критично низький — система вже надіслала push-сповіщення менеджеру.'
            },
            {
                sku: 'TS-772',
                name: 'Футболка oversize',
                price: '₴280',
                stock: 120,
                category: 'Одяг',
                visibility: 'active',
                visibilityLabel: 'Активний',
                sales30: 312,
                desc: 'Топ-1 за кількістю замовлень за останні 30 днів. Автопідняття в каталозі увімкнено.'
            },
            {
                sku: 'SK-009',
                name: 'Шкарпетки бавовняні',
                price: '₴75',
                stock: 340,
                category: 'Аксесуари',
                visibility: 'active',
                visibilityLabel: 'Активний',
                sales30: 89,
                desc: 'Допродаж у кошику. Пакетна ціна та знижка від 3 пар працюють автоматично.'
            }
        ],
        analyticsTop: [
            { name: 'Кросівки Nike Air', sales: 128, revenue: '₴126k' },
            { name: 'Куртка зимова', sales: 54, revenue: '₴156k' },
            { name: 'Футболка oversize', sales: 312, revenue: '₴87k' },
            { name: 'Сумка шкіряна', sales: 41, revenue: '₴36k' },
            { name: 'Годинник Casio', sales: 22, revenue: '₴47k' }
        ]
    };


    function applyRuLocale() {
        if (!isRu) return;

        STATUS_META.paid.label = 'Оплачено';
        STATUS_META.pending.label = 'В обработке';
        STATUS_META.shipped.label = 'Отправлено';

        TITLE_MAP.orders = 'Админ / Заказы';
        TITLE_MAP.products = 'Админ / Товары';
        TITLE_MAP.analytics = 'Админ / Аналитика';

        state.orders = [
            {
                id: '10428',
                customer: 'Елена К.',
                sum: '₴1 290',
                status: 'paid',
                phone: '+380 67 123 45 67',
                email: 'olena.k@email.com',
                items: [
                    { name: 'Кроссовки Nike Air', qty: 1, price: '₴990' },
                    { name: 'Носки хлопковые', qty: 2, price: '₴150' }
                ]
            },
            {
                id: '10427',
                customer: 'Андрей М.',
                sum: '₴3 099',
                status: 'pending',
                phone: '+380 50 987 65 43',
                email: 'andriy.m@email.com',
                items: [
                    { name: 'Куртка зимняя', qty: 1, price: '₴2 509' },
                    { name: 'Шарф', qty: 1, price: '₴590' }
                ]
            },
            {
                id: '10426',
                customer: 'Ирина В.',
                sum: '₴1 999',
                status: 'shipped',
                phone: '+380 93 456 78 90',
                email: 'iryna.v@email.com',
                items: [
                    { name: 'Сумка кожаная', qty: 1, price: '₴1 999' }
                ]
            },
            {
                id: '10425',
                customer: 'Максим Е.',
                sum: '₴2 489',
                status: 'paid',
                phone: '+380 66 234 56 78',
                email: 'max.t@email.com',
                items: [
                    { name: 'Часы Casio', qty: 1, price: '₴2 489' }
                ]
            },
            {
                id: '10424',
                customer: 'София Л.',
                sum: '₴690',
                status: 'pending',
                phone: '+380 97 345 67 89',
                email: 'sofia.l@email.com',
                items: [
                    { name: 'Футболка oversize', qty: 2, price: '₴345' }
                ]
            }
        ];

        state.products = [
            {
                sku: 'NK-001',
                name: 'Кроссовки Nike Air',
                price: '₴990',
                stock: 42,
                category: 'Обувь',
                visibility: 'active',
                visibilityLabel: 'Активный',
                sales30: 128,
                desc: 'Бестселлер категории. Синхронизация с Prom и Rozetka без ручного обновления.'
            },
            {
                sku: 'JK-204',
                name: 'Куртка зимняя',
                price: '₴2 890',
                stock: 8,
                category: 'Одежда',
                visibility: 'active',
                visibilityLabel: 'Активный',
                sales30: 54,
                desc: 'Премиум-позиция с высоким средним чеком. Остатки обновляются после каждого заказа.'
            },
            {
                sku: 'BG-118',
                name: 'Сумка кожаная',
                price: '₴890',
                stock: 15,
                category: 'Аксессуары',
                visibility: 'active',
                visibilityLabel: 'Активный',
                sales30: 41,
                desc: 'Стабильные продажи с органического трафика. SEO-карточка оптимизирована под Google Shopping.'
            },
            {
                sku: 'CS-440',
                name: 'Часы Casio',
                price: '₴2 150',
                stock: 3,
                category: 'Аксессуары',
                visibility: 'low',
                visibilityLabel: 'Мало на складе',
                sales30: 22,
                desc: 'Остаток критически низкий — система уже отправила push-уведомление менеджеру.'
            },
            {
                sku: 'TS-772',
                name: 'Футболка oversize',
                price: '₴280',
                stock: 120,
                category: 'Одежда',
                visibility: 'active',
                visibilityLabel: 'Активный',
                sales30: 312,
                desc: 'Топ-1 по количеству заказов за последние 30 дней. Автоподнятие в каталоге включено.'
            },
            {
                sku: 'SK-009',
                name: 'Носки хлопковые',
                price: '₴75',
                stock: 340,
                category: 'Аксессуары',
                visibility: 'active',
                visibilityLabel: 'Активный',
                sales30: 89,
                desc: 'Допродажа в корзине. Пакетная цена и скидка от 3 пар работают автоматически.'
            }
        ];

        state.analyticsTop = [
            { name: 'Кроссовки Nike Air', sales: 128, revenue: '₴126k' },
            { name: 'Куртка зимняя', sales: 54, revenue: '₴156k' },
            { name: 'Футболка oversize', sales: 312, revenue: '₴87k' },
            { name: 'Сумка кожаная', sales: 41, revenue: '₴36k' },
            { name: 'Часы Casio', sales: 22, revenue: '₴47k' }
        ];
    }

    applyRuLocale();

    function initAdminMock() {
        var mock = document.querySelector('[data-admin-mock]');
        if (!mock) return;

        var panel = mock.querySelector('#pl-admin-panel');
        var titleEl = mock.querySelector('#pl-admin-title');
        var backBtn = mock.querySelector('#pl-admin-back');
        var tabBtns = mock.querySelectorAll('[data-admin-tab]');
        if (!panel || !titleEl) return;

        var reduceMotion = window.matchMedia &&
            window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        var historyStack = [{ view: 'orders' }];
        var activeTab = 'orders';
        var animating = false;

        function escapeHtml(str) {
            return String(str)
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;');
        }

        function getOrder(id) {
            for (var i = 0; i < state.orders.length; i += 1) {
                if (state.orders[i].id === id) return state.orders[i];
            }
            return null;
        }

        function getProduct(sku) {
            for (var i = 0; i < state.products.length; i += 1) {
                if (state.products[i].sku === sku) return state.products[i];
            }
            return null;
        }

        function isDetailView() {
            var view = getCurrentView().view;
            return view === 'order-detail' || view === 'product-detail';
        }

        function syncProductVisibility(product) {
            if (product.stock <= 0) {
                product.visibility = 'out';
                product.visibilityLabel = isRu ? 'Нет в наличии' : 'Немає в наявності';
                return;
            }
            if (product.stock <= 5) {
                product.visibility = 'low';
                product.visibilityLabel = isRu ? 'Мало на складе' : 'Мало на складі';
                return;
            }
            product.visibility = 'active';
            product.visibilityLabel = isRu ? 'Активный' : 'Активний';
        }

        function nextStatus(current) {
            var idx = STATUS_CYCLE.indexOf(current);
            return STATUS_CYCLE[(idx + 1) % STATUS_CYCLE.length];
        }

        function renderStatusButton(order) {
            var meta = STATUS_META[order.status];
            return '<button type="button" class="pl-shop__status ' + meta.className +
                '" data-admin-status="' + escapeHtml(order.id) +
                '" aria-label="' + (isRu ? 'Изменить статус заказа #' : 'Змінити статус замовлення #') + escapeHtml(order.id) + '">' +
                escapeHtml(meta.label) + '</button>';
        }

        function renderMetrics(metricsHtml) {
            return '<div class="pl-shop__admin-metrics">' + metricsHtml + '</div>';
        }

        function renderMetric(label, value, extraClass) {
            return '<div class="pl-shop__admin-metric">' +
                '<div class="pl-shop__admin-metric-label">' + escapeHtml(label) + '</div>' +
                '<div class="pl-shop__admin-metric-val' + (extraClass ? ' ' + extraClass : '') + '">' +
                escapeHtml(value) + '</div></div>';
        }

        function renderChartMetric() {
            var src = mock.getAttribute('data-chart-src');
            var srcMobile = mock.getAttribute('data-chart-src-mobile');
            var chart = src
                ? '<picture class="pl-shop__admin-chart" aria-hidden="true">' +
                    (srcMobile ? '<source media="(max-width: 767px)" srcset="' + escapeHtml(srcMobile) + '">' : '') +
                    '<img src="' + escapeHtml(src) + '" alt="" width="160" height="94" decoding="async"></picture>'
                : '';
            return '<div class="pl-shop__admin-metric pl-shop__admin-metric--chart">' +
                '<div class="pl-shop__admin-metric-label">' + (isRu ? 'Конверсия' : 'Конверсія') + '</div>' +
                chart + '</div>';
        }

        function renderAnalyticsBars() {
            var heights = [35, 55, 42, 78, 100];
            var html = '<div class="pl-shop__admin-metric pl-shop__admin-metric--wide">' +
                '<div class="pl-shop__admin-metric-label">' + (isRu ? 'Продажи за неделю' : 'Продажі за тиждень') + '</div>' +
                '<div class="pl-shop__admin-bars pl-shop__admin-bars--tall" aria-hidden="true">';
            heights.forEach(function (h, i) {
                var acc = i >= 3 ? ' pl-shop__admin-bar-col--acc' : '';
                html += '<span class="pl-shop__admin-bar-col' + acc + '" style="height:' + h + '%"></span>';
            });
            html += '</div></div>';
            return html;
        }

        function renderTableHead(cols) {
            var html = '<div class="pl-shop__admin-table-head">';
            cols.forEach(function (col) {
                html += '<span class="' + col.className + '">' + escapeHtml(col.label) + '</span>';
            });
            html += '</div>';
            return html;
        }

        function renderOrdersView() {
            var metrics = renderMetrics(
                renderMetric(isRu ? 'Заказов сегодня' : 'Замовлень сьогодні', '47') +
                renderMetric(isRu ? 'Выручка' : 'Виручка', '₴84k', 'pl-shop__admin-metric-val--acc') +
                renderChartMetric()
            );

            var rows = '';
            state.orders.forEach(function (order, i) {
                rows += '<div class="pl-shop__admin-table-row pl-shop__admin-table-row--clickable" role="button" tabindex="0" data-admin-order="' +
                    escapeHtml(order.id) + '" style="--admin-row-i:' + i + '">' +
                    '<span class="pl-shop__admin-col-order"><span class="pl-shop__admin-order-id">#' + escapeHtml(order.id) + '</span>' +
                    '<span class="pl-shop__admin-order-dot" aria-hidden="true"></span>' +
                    '<span class="pl-shop__admin-order-name">' + escapeHtml(order.customer) + '</span></span>' +
                    '<span class="pl-shop__admin-col-sum">' + escapeHtml(order.sum) + '</span>' +
                    '<span class="pl-shop__admin-col-status">' + renderStatusButton(order) + '</span>' +
                    '</div>';
            });

            return metrics +
                '<div class="pl-shop__admin-table-wrap">' +
                '<div class="pl-shop__admin-table">' +
                renderTableHead([
                    { className: 'pl-shop__admin-col-order', label: isRu ? 'Заказы' : 'Замовлення' },
                    { className: 'pl-shop__admin-col-sum', label: isRu ? 'Сумма' : 'Сума' },
                    { className: 'pl-shop__admin-col-status', label: isRu ? 'Статус' : 'Статус' }
                ]) + rows + '</div></div>';
        }

        function renderProductsView() {
            var metrics = renderMetrics(
                renderMetric(isRu ? 'SKU в каталоге' : 'SKU в каталозі', '1 248') +
                renderMetric(isRu ? 'На складе' : 'На складі', '892', 'pl-shop__admin-metric-val--acc') +
                renderMetric(isRu ? 'Новых за неделю' : 'Нових за тиждень', '12')
            );

            var rows = '';
            state.products.forEach(function (product, i) {
                rows += '<div class="pl-shop__admin-table-row pl-shop__admin-table-row--clickable" role="button" tabindex="0" data-admin-product="' +
                    escapeHtml(product.sku) + '" aria-label="' + (isRu ? 'Открыть карточку товара ' : 'Відкрити картку товару ') + escapeHtml(product.name) +
                    '" style="--admin-row-i:' + i + '">' +
                    '<span class="pl-shop__admin-col-order">' + escapeHtml(product.name) + '</span>' +
                    '<span class="pl-shop__admin-col-sum">' + escapeHtml(product.price) + '</span>' +
                    '<span class="pl-shop__admin-col-status pl-shop__admin-col-stock">' + escapeHtml(String(product.stock)) + (isRu ? ' шт.</span>' : ' од.</span>') +
                    '</div>';
            });

            return metrics +
                '<div class="pl-shop__admin-table-wrap">' +
                '<div class="pl-shop__admin-table">' +
                renderTableHead([
                    { className: 'pl-shop__admin-col-order', label: isRu ? 'Товар' : 'Товар' },
                    { className: 'pl-shop__admin-col-sum', label: isRu ? 'Цена' : 'Ціна' },
                    { className: 'pl-shop__admin-col-status', label: isRu ? 'Остаток' : 'Залишок' }
                ]) + rows + '</div></div>';
        }

        function renderAnalyticsView() {
            var metrics = renderMetrics(
                renderMetric(isRu ? 'Посетители' : 'Відвідувачі', '2 840') +
                renderMetric(isRu ? 'Конверсия' : 'Конверсія', '3.2%', 'pl-shop__admin-metric-val--acc') +
                renderMetric(isRu ? 'Средний чек' : 'Середній чек', '₴1 840')
            );

            var rows = '';
            state.analyticsTop.forEach(function (item, i) {
                rows += '<div class="pl-shop__admin-table-row" style="--admin-row-i:' + i + '">' +
                    '<span class="pl-shop__admin-col-order">' + escapeHtml(item.name) + '</span>' +
                    '<span class="pl-shop__admin-col-sum">' + escapeHtml(String(item.sales)) + '</span>' +
                    '<span class="pl-shop__admin-col-status pl-shop__admin-col-stock">' + escapeHtml(item.revenue) + '</span>' +
                    '</div>';
            });

            return metrics + renderAnalyticsBars() +
                '<div class="pl-shop__admin-table-wrap">' +
                '<div class="pl-shop__admin-table">' +
                renderTableHead([
                    { className: 'pl-shop__admin-col-order', label: isRu ? 'Топ товар' : 'Топ товар' },
                    { className: 'pl-shop__admin-col-sum', label: isRu ? 'Продажи' : 'Продажі' },
                    { className: 'pl-shop__admin-col-status', label: isRu ? 'Выручка' : 'Виручка' }
                ]) + rows + '</div></div>';
        }

        function renderOrderDetail(orderId) {
            var order = getOrder(orderId);
            if (!order) return renderOrdersView();

            var itemsHtml = '';
            order.items.forEach(function (item, i) {
                itemsHtml += '<div class="pl-shop__admin-detail-item" style="--admin-row-i:' + i + '">' +
                    '<span class="pl-shop__admin-detail-item-name">' + escapeHtml(item.name) + '</span>' +
                    '<span class="pl-shop__admin-detail-item-qty">×' + escapeHtml(String(item.qty)) + '</span>' +
                    '<span class="pl-shop__admin-detail-item-price">' + escapeHtml(item.price) + '</span>' +
                    '</div>';
            });

            return '<div class="pl-shop__admin-detail">' +
                '<div class="pl-shop__admin-detail-head">' +
                '<p class="pl-shop__admin-detail-name">' + escapeHtml(order.customer) + '</p>' +
                '<p class="pl-shop__admin-detail-meta">' + escapeHtml(order.phone) + ' · ' + escapeHtml(order.email) + '</p>' +
                '<div class="pl-shop__admin-detail-status">' + renderStatusButton(order) + '</div>' +
                '</div>' +
                '<div class="pl-shop__admin-detail-items">' + itemsHtml + '</div>' +
                '<div class="pl-shop__admin-detail-total">' +
                '<span>' + (isRu ? 'Итого' : 'Разом') + '</span><strong>' + escapeHtml(order.sum) + '</strong>' +
                '</div></div>';
        }

        function renderProductBadge(product) {
            return '<span class="pl-shop__admin-product-badge pl-shop__admin-product-badge--' +
                escapeHtml(product.visibility) + '">' + escapeHtml(product.visibilityLabel) + '</span>';
        }

        function renderProductDetail(sku) {
            var product = getProduct(sku);
            if (!product) return renderProductsView();

            return '<div class="pl-shop__admin-detail pl-shop__admin-detail--product">' +
                '<div class="pl-shop__admin-detail-head">' +
                '<p class="pl-shop__admin-detail-name">' + escapeHtml(product.name) + '</p>' +
                '<p class="pl-shop__admin-detail-meta">SKU ' + escapeHtml(product.sku) + ' · ' + escapeHtml(product.category) + '</p>' +
                '<div class="pl-shop__admin-detail-status">' + renderProductBadge(product) + '</div>' +
                '</div>' +
                '<div class="pl-shop__admin-detail-specs">' +
                '<div class="pl-shop__admin-detail-spec" style="--admin-row-i:0">' +
                '<span class="pl-shop__admin-detail-spec-label">' + (isRu ? 'Цена' : 'Ціна') + '</span>' +
                '<strong class="pl-shop__admin-detail-spec-val">' + escapeHtml(product.price) + '</strong></div>' +
                '<div class="pl-shop__admin-detail-spec" style="--admin-row-i:1">' +
                '<span class="pl-shop__admin-detail-spec-label">' + (isRu ? 'Остаток' : 'Залишок') + '</span>' +
                '<strong class="pl-shop__admin-detail-spec-val" data-admin-stock-val="' + escapeHtml(product.sku) + '">' +
                escapeHtml(String(product.stock)) + (isRu ? ' шт.</strong></div>' : ' од.</strong></div>') +
                '<div class="pl-shop__admin-detail-spec" style="--admin-row-i:2">' +
                '<span class="pl-shop__admin-detail-spec-label">' + (isRu ? 'Продажи / 30 дн' : 'Продажі / 30 дн') + '</span>' +
                '<strong class="pl-shop__admin-detail-spec-val pl-shop__admin-detail-spec-val--acc">' +
                escapeHtml(String(product.sales30)) + '</strong></div>' +
                '</div>' +
                '<p class="pl-shop__admin-detail-desc">' + escapeHtml(product.desc) + '</p>' +
                '<div class="pl-shop__admin-stock-control">' +
                '<span class="pl-shop__admin-stock-label">' + (isRu ? 'Обновить остаток' : 'Оновити залишок') + '</span>' +
                '<div class="pl-shop__admin-stock-actions">' +
                '<button type="button" class="pl-shop__admin-stock-btn" data-admin-stock-minus="' + escapeHtml(product.sku) +
                '" aria-label="' + (isRu ? 'Уменьшить остаток' : 'Зменшити залишок') + '">−</button>' +
                '<button type="button" class="pl-shop__admin-stock-btn pl-shop__admin-stock-btn--plus" data-admin-stock-plus="' +
                escapeHtml(product.sku) + '" aria-label="' + (isRu ? 'Увеличить остаток' : 'Збільшити залишок') + '">+</button>' +
                '</div></div></div>';
        }

        function getCurrentView() {
            return historyStack[historyStack.length - 1];
        }

        function updateChrome(viewState) {
            if (viewState.view === 'order-detail') {
                titleEl.textContent = (isRu ? 'Админ / Заказы #' : 'Адмін / Замовлення #') + viewState.id;
                if (backBtn) backBtn.hidden = false;
                tabBtns.forEach(function (btn) {
                    btn.setAttribute('aria-disabled', 'true');
                    btn.tabIndex = -1;
                });
                return;
            }

            if (viewState.view === 'product-detail') {
                var product = getProduct(viewState.id);
                titleEl.textContent = product
                    ? (isRu ? 'Админ / ' : 'Адмін / ') + product.name
                    : (isRu ? 'Админ / Товар' : 'Адмін / Товар');
                if (backBtn) backBtn.hidden = false;
                tabBtns.forEach(function (btn) {
                    btn.setAttribute('aria-disabled', 'true');
                    btn.tabIndex = -1;
                });
                return;
            }

            if (backBtn) backBtn.hidden = true;
            tabBtns.forEach(function (btn) {
                btn.removeAttribute('aria-disabled');
                btn.tabIndex = 0;
                var tab = btn.getAttribute('data-admin-tab');
                var selected = tab === viewState.view;
                btn.setAttribute('aria-selected', selected ? 'true' : 'false');
                btn.classList.toggle('pl-shop__admin-nav-btn--active', selected);
            });
            titleEl.textContent = TITLE_MAP[viewState.view] || TITLE_MAP.orders;
        }

        function renderContent(viewState, animate) {
            var html;
            if (viewState.view === 'order-detail') {
                html = renderOrderDetail(viewState.id);
            } else if (viewState.view === 'product-detail') {
                html = renderProductDetail(viewState.id);
            } else if (viewState.view === 'products') {
                html = renderProductsView();
            } else if (viewState.view === 'analytics') {
                html = renderAnalyticsView();
            } else {
                html = renderOrdersView();
            }

            updateChrome(viewState);

            if (!animate || reduceMotion) {
                panel.innerHTML = html;
                panel.classList.remove('pl-shop__admin-panel--exit', 'pl-shop__admin-panel--enter');
                return;
            }

            if (animating) return;
            animating = true;
            panel.classList.add('pl-shop__admin-panel--exit');

            setTimeout(function () {
                panel.innerHTML = html;
                panel.classList.remove('pl-shop__admin-panel--exit');
                panel.classList.add('pl-shop__admin-panel--enter');
                setTimeout(function () {
                    panel.classList.remove('pl-shop__admin-panel--enter');
                    animating = false;
                }, 380);
            }, 180);
        }

        function switchTab(tabId) {
            if (isDetailView()) return;
            activeTab = tabId;
            historyStack = [{ view: tabId }];
            renderContent({ view: tabId }, true);
        }

        function openOrderDetail(orderId) {
            historyStack.push({ view: 'order-detail', id: orderId });
            renderContent(getCurrentView(), true);
        }

        function openProductDetail(sku) {
            historyStack.push({ view: 'product-detail', id: sku });
            renderContent(getCurrentView(), true);
        }

        function goBack() {
            if (historyStack.length <= 1) return;
            historyStack.pop();
            renderContent(getCurrentView(), true);
        }

        function toggleStatus(orderId, btn) {
            var order = getOrder(orderId);
            if (!order) return;
            order.status = nextStatus(order.status);
            var meta = STATUS_META[order.status];
            btn.className = 'pl-shop__status ' + meta.className;
            btn.textContent = meta.label;
            btn.setAttribute('aria-label', (isRu ? 'Изменить статус заказа #' : 'Змінити статус замовлення #') + orderId);
            if (!reduceMotion) {
                btn.classList.add('pl-shop__status--changing');
                setTimeout(function () {
                    btn.classList.remove('pl-shop__status--changing');
                }, 420);
            }
        }

        function updateProductDetailStock(product) {
            syncProductVisibility(product);
            var stockEl = panel.querySelector('[data-admin-stock-val="' + product.sku + '"]');
            if (stockEl) {
                stockEl.textContent = product.stock + (isRu ? ' шт.' : ' од.');
                if (!reduceMotion) {
                    stockEl.classList.add('pl-shop__admin-stock-val--changing');
                    setTimeout(function () {
                        stockEl.classList.remove('pl-shop__admin-stock-val--changing');
                    }, 420);
                }
            }
            var badgeEl = panel.querySelector('.pl-shop__admin-product-badge');
            if (badgeEl) {
                badgeEl.className = 'pl-shop__admin-product-badge pl-shop__admin-product-badge--' + product.visibility;
                badgeEl.textContent = product.visibilityLabel;
            }
        }

        function adjustStock(sku, delta) {
            var product = getProduct(sku);
            if (!product) return;
            product.stock = Math.max(0, product.stock + delta);
            updateProductDetailStock(product);
            var btn = panel.querySelector('[data-admin-stock-' + (delta > 0 ? 'plus' : 'minus') + '="' + sku + '"]');
            if (btn && !reduceMotion) {
                btn.classList.add('pl-shop__admin-stock-btn--changing');
                setTimeout(function () {
                    btn.classList.remove('pl-shop__admin-stock-btn--changing');
                }, 320);
            }
        }

        tabBtns.forEach(function (btn) {
            btn.addEventListener('click', function () {
                switchTab(btn.getAttribute('data-admin-tab'));
            });
        });

        mock.addEventListener('keydown', function (event) {
            if (isDetailView()) return;
            if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
            var tabs = ['orders', 'products', 'analytics'];
            var idx = tabs.indexOf(activeTab);
            if (idx < 0) return;
            if (event.key === 'ArrowRight') idx = (idx + 1) % tabs.length;
            else idx = (idx - 1 + tabs.length) % tabs.length;
            var nextBtn = mock.querySelector('[data-admin-tab="' + tabs[idx] + '"]');
            if (nextBtn) {
                nextBtn.focus();
                switchTab(tabs[idx]);
            }
        });

        if (backBtn) {
            backBtn.addEventListener('click', goBack);
        }

        panel.addEventListener('click', function (event) {
            var statusBtn = event.target.closest('[data-admin-status]');
            if (statusBtn) {
                event.stopPropagation();
                event.preventDefault();
                toggleStatus(statusBtn.getAttribute('data-admin-status'), statusBtn);
                return;
            }

            var orderBtn = event.target.closest('[data-admin-order]');
            if (orderBtn) {
                openOrderDetail(orderBtn.getAttribute('data-admin-order'));
                return;
            }

            var productBtn = event.target.closest('[data-admin-product]');
            if (productBtn) {
                openProductDetail(productBtn.getAttribute('data-admin-product'));
                return;
            }

            var stockMinus = event.target.closest('[data-admin-stock-minus]');
            if (stockMinus) {
                event.stopPropagation();
                adjustStock(stockMinus.getAttribute('data-admin-stock-minus'), -1);
                return;
            }

            var stockPlus = event.target.closest('[data-admin-stock-plus]');
            if (stockPlus) {
                event.stopPropagation();
                adjustStock(stockPlus.getAttribute('data-admin-stock-plus'), 1);
            }
        });

        panel.addEventListener('keydown', function (event) {
            if (event.key !== 'Enter' && event.key !== ' ') return;

            var orderBtn = event.target.closest('[data-admin-order]');
            if (orderBtn) {
                event.preventDefault();
                openOrderDetail(orderBtn.getAttribute('data-admin-order'));
                return;
            }

            var productBtn = event.target.closest('[data-admin-product]');
            if (!productBtn) return;
            event.preventDefault();
            openProductDetail(productBtn.getAttribute('data-admin-product'));
        });

        renderContent({ view: 'orders' }, false);
    }

    window.initAdminMock = initAdminMock;
})();
