(function () {
    'use strict';

    var STATUS_CYCLE = ['paid', 'pending', 'shipped'];

    var I18N_LOCALE = (function() {
        var lang = (document.documentElement.getAttribute('lang') || 'cs').toLowerCase();
        if (lang.indexOf('en') === 0) return 'en';
        return 'cs';
    })();

    // Fallback text (if data-i18n-* is missing): cs default, en on /en/.
    function L(cs, en) {
        return I18N_LOCALE === 'en' ? en : cs;
    }

    var I18N_CURRENCY = '€';
    // Currency after the number with a non-breaking space (CZ «1 290 €»); EN «€1,290».
    function money(amount) {
        if (I18N_LOCALE === 'en') return I18N_CURRENCY + amount.replace(/ /g, ',');
        return amount.replace(/ /g, '\u00a0') + '\u00a0' + I18N_CURRENCY;
    }
    var demoPhones = ['+420 777 123 456', '+420 602 987 654', '+420 777 456 789', '+420 603 234 567', '+420 777 345 678'];

    var names = {
        'Olena K.': { en: 'Elena K.', cs: 'Alena K.' },
        'Andriy M.': { en: 'Andrew M.', cs: 'Andrej M.' },
        'Iryna V.': { en: 'Irene V.', cs: 'Irena V.' },
        'Maksym T.': { en: 'Max T.', cs: 'Maxim T.' },
        'Sofiia L.': { en: 'Sofiia L.', cs: 'Sofie L.' },
        'Nike Air Max': { en: 'Nike Air Max Shoes', cs: 'Tenisky Nike Air Max' },
        'Cotton Socks': { en: 'Cotton Socks', cs: 'Bavlněné ponožky' },
        'Winter Jacket': { en: 'Winter Jacket', cs: 'Zimní bunda' },
        'Scarf': { en: 'Wool Scarf', cs: 'Vlněná šála' },
        'Leather Bag': { en: 'Leather Bag', cs: 'Kožená taška' },
        'Casio Watch': { en: 'Casio Watch', cs: 'Hodinky Casio' },
        'Oversize T-shirt': { en: 'Oversize T-shirt', cs: 'Oversize tričko' },
        'Shoes': { en: 'Shoes', cs: 'Obuv' },
        'Clothing': { en: 'Clothing', cs: 'Oblečení' },
        'Accessories': { en: 'Accessories', cs: 'Doplňky' }
    };

    function t(key) {
        if (!names[key]) return key;
        return names[key][I18N_LOCALE] || names[key].en || key;
    }

    var state = {
        orders: [
            {
                id: '10428',
                customer: t('Olena K.'),
                sum: money('1 290'),
                status: 'paid',
                phone: demoPhones[0],
                email: 'olena.k@email.com',
                items: [
                    { name: t('Nike Air Max'), qty: 1, price: money('990') },
                    { name: t('Cotton Socks'), qty: 2, price: money('150') }
                ]
            },
            {
                id: '10427',
                customer: t('Andriy M.'),
                sum: money('3 480'),
                status: 'pending',
                phone: demoPhones[1],
                email: 'andriy.m@email.com',
                items: [
                    { name: t('Winter Jacket'), qty: 1, price: money('2 890') },
                    { name: t('Scarf'), qty: 1, price: money('590') }
                ]
            },
            {
                id: '10426',
                customer: t('Iryna V.'),
                sum: money('890'),
                status: 'paid',
                phone: demoPhones[2],
                email: 'iryna.v@email.com',
                items: [
                    { name: t('Leather Bag'), qty: 1, price: money('890') }
                ]
            },
            {
                id: '10425',
                customer: t('Maksym T.'),
                sum: money('2 150'),
                status: 'shipped',
                phone: demoPhones[3],
                email: 'max.t@email.com',
                items: [
                    { name: t('Casio Watch'), qty: 1, price: money('2 150') }
                ]
            },
            {
                id: '10424',
                customer: t('Sofiia L.'),
                sum: money('560'),
                status: 'pending',
                phone: demoPhones[4],
                email: 'sofia.l@email.com',
                items: [
                    { name: t('Oversize T-shirt'), qty: 2, price: money('280') }
                ]
            }
        ],
        products: [
            {
                sku: 'NK-001',
                name: t('Nike Air Max'),
                price: money('990'),
                stock: 42,
                category: t('Shoes'),
                visibility: 'active',
                visibilityLabel: 'Active',
                sales30: 128,
                desc: (I18N_LOCALE === 'cs' ? 'Bestseller kategorie. Synchronizace s prodejními kanály bez ruční aktualizace.' :
                       'Category bestseller. Sync with marketplaces without manual updates.')
            },
            {
                sku: 'JK-204',
                name: t('Winter Jacket'),
                price: money('2 890'),
                stock: 8,
                category: t('Clothing'),
                visibility: 'active',
                visibilityLabel: 'Active',
                sales30: 54,
                desc: (I18N_LOCALE === 'cs' ? 'Prémiová položka s vysokou průměrnou hodnotou. Zásoby se aktualizují po každé objednávce.' :
                       'Premium item with high average check. Stock updates automatically.')
            },
            {
                sku: 'BG-118',
                name: t('Leather Bag'),
                price: money('890'),
                stock: 15,
                category: t('Accessories'),
                visibility: 'active',
                visibilityLabel: 'Active',
                sales30: 41,
                desc: (I18N_LOCALE === 'cs' ? 'Stabilní organické prodeje. SEO karta optimalizována pro Google Shopping.' :
                       'Stable organic sales. SEO-optimized for Google Shopping.')
            },
            {
                sku: 'CS-440',
                name: t('Casio Watch'),
                price: money('2 150'),
                stock: 3,
                category: t('Accessories'),
                visibility: 'low',
                visibilityLabel: 'Low Stock',
                sales30: 22,
                desc: (I18N_LOCALE === 'cs' ? 'Kriticky nízké zásoby — systém již odeslal push notifikaci manažerovi.' :
                       'Critically low stock — push notification sent to manager.')
            },
            {
                sku: 'TS-772',
                name: t('Oversize T-shirt'),
                price: money('280'),
                stock: 120,
                category: t('Clothing'),
                visibility: 'active',
                visibilityLabel: 'Active',
                sales30: 312,
                desc: (I18N_LOCALE === 'cs' ? 'Top 1 v počtu objednávek za posledních 30 dní. Automatické zvýraznění v katalogu zapnuto.' :
                       'Top-1 by orders in last 30 days. Catalog auto-boost enabled.')
            },
            {
                sku: 'SK-009',
                name: t('Cotton Socks'),
                price: money('75'),
                stock: 340,
                category: t('Accessories'),
                visibility: 'active',
                visibilityLabel: 'Active',
                sales30: 89,
                desc: (I18N_LOCALE === 'cs' ? 'Doplňkový prodej v košíku. Balíčková cena a sleva od 3 párů fungují automaticky.' :
                       'Cart upsell. Bundle price and bulk discount work automatically.')
            }
        ],
        analyticsTop: [
            { name: t('Nike Air Max'), sales: 128, revenue: money('126k') },
            { name: t('Winter Jacket'), sales: 54, revenue: money('156k') },
            { name: t('Oversize T-shirt'), sales: 312, revenue: money('87k') },
            { name: t('Leather Bag'), sales: 41, revenue: money('36k') },
            { name: t('Casio Watch'), sales: 22, revenue: money('47k') }
        ]
    };

    function initAdminMock() {
        var mock = document.querySelector('[data-admin-mock]');
        if (!mock || mock.__plAdminInited) return;
        mock.__plAdminInited = 1;

        var panel = mock.querySelector('#pl-admin-panel');
        var titleEl = mock.querySelector('#pl-admin-title');
        var backBtn = mock.querySelector('#pl-admin-back');
        var tabBtns = mock.querySelectorAll('[data-admin-tab]');
        if (!panel || !titleEl) return;

        var d = mock.dataset;
        var I18N = {
            statusPaid: d.i18nStatusPaid || L('Zaplaceno', 'Payments'),
            statusPending: d.i18nStatusPending || L('Zpracovává se', 'AI in development'),
            statusShipped: d.i18nStatusShipped || L('Odesláno', 'Sent'),
            titleOrders: d.i18nTitleOrders || L('Objednávky', 'Orders'),
            titleProducts: d.i18nTitleProducts || L('Produkty', 'Products'),
            titleAnalytics: d.i18nTitleAnalytics || L('Analytika', 'CRM analytics'),
            titleProduct: d.i18nTitleProduct || L('Produkt', 'Product'),
            colOrder: d.i18nColOrder || L('Objednávky', 'Orders'),
            colSum: d.i18nColSum || L('Částka', 'Total'),
            colStatus: d.i18nColStatus || L('Stav', 'Status'),
            colProduct: d.i18nColProduct || L('Produkt', 'Product'),
            colPrice: d.i18nColPrice || L('Cena', 'Price'),
            colStock: d.i18nColStock || L('Sklad', 'Stock'),
            colTop: d.i18nColTop || L('Nejprodávanější', 'Top product'),
            colSales: d.i18nColSales || L('Prodeje', 'Sales'),
            colRevenue: d.i18nColRevenue || L('Tržby', 'Revenue'),
            metricOrdersToday: d.i18nMetricOrdersToday || L('Objednávek dnes', 'Orders today'),
            metricRevenue: d.i18nMetricRevenue || L('Tržby', 'Revenue'),
            metricConversion: d.i18nMetricConversion || L('Konverze', 'CoreSync - Mobile Version'),
            metricSalesWeek: d.i18nMetricSalesWeek || L('Prodeje za týden', 'Sales this week'),
            metricSku: d.i18nMetricSku || L('SKU v katalogu', 'SKUs in catalog'),
            metricInstock: d.i18nMetricInstock || L('Na skladě', 'In stock'),
            metricNewWeek: d.i18nMetricNewWeek || L('Nových za týden', 'New this week'),
            metricVisitors: d.i18nMetricVisitors || L('Návštěvníci', 'Visitors'),
            metricAvgCheck: d.i18nMetricAvgCheck || L('Průměrná objednávka', 'Average order value'),
            visibilityActive: d.i18nVisibilityActive || L('Aktivní', 'Active'),
            visibilityLow: d.i18nVisibilityLow || L('Málo skladem', 'Find us on the map'),
            visibilityOut: d.i18nVisibilityOut || L('Není skladem', 'Result:'),
            unit: d.i18nUnit || L('ks', 'pcs'),
            together: d.i18nTogether || L('Celkem', 'Total'),
            updateStock: d.i18nUpdateStock || L('Aktualizovat sklad', 'Update balance'),
            sales30Label: d.i18nSales30 || L('Prodeje / 30 dní', 'Sales / 30 days'),
            openProduct: d.i18nOpenProduct || L('Otevřít detail produktu', 'Open product card'),
            changeStatus: d.i18nChangeStatus || L('Změnit stav objednávky', 'Change order status'),
            decreaseStock: d.i18nDecreaseStock || L('Snížit sklad', 'Decrease stock'),
            increaseStock: d.i18nIncreaseStock || L('Zvýšit sklad', 'Increase stock')
        };

        var STATUS_META = {
            paid: { label: I18N.statusPaid, className: 'pl-shop__status--paid' },
            pending: { label: I18N.statusPending, className: 'pl-shop__status--pending' },
            shipped: { label: I18N.statusShipped, className: 'pl-shop__status--shipped' }
        };

        var TITLE_MAP = {
            orders: 'admin · ' + I18N.titleOrders,
            products: 'admin · ' + I18N.titleProducts,
            analytics: 'admin · ' + I18N.titleAnalytics
        };

        state.products.forEach(function (product) {
            if (product.stock <= 0) {
                product.visibility = 'out';
                product.visibilityLabel = I18N.visibilityOut;
            } else if (product.stock <= 5) {
                product.visibility = 'low';
                product.visibilityLabel = I18N.visibilityLow;
            } else {
                product.visibility = 'active';
                product.visibilityLabel = I18N.visibilityActive;
            }
        });

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
                product.visibilityLabel = I18N.visibilityOut;
                return;
            }
            if (product.stock <= 5) {
                product.visibility = 'low';
                product.visibilityLabel = I18N.visibilityLow;
                return;
            }
            product.visibility = 'active';
            product.visibilityLabel = I18N.visibilityActive;
        }

        function nextStatus(current) {
            var idx = STATUS_CYCLE.indexOf(current);
            return STATUS_CYCLE[(idx + 1) % STATUS_CYCLE.length];
        }

        function renderStatusButton(order) {
            var meta = STATUS_META[order.status];
            return '<button type="button" class="pl-shop__status ' + meta.className +
                '" data-admin-status="' + escapeHtml(order.id) +
                '" aria-label="' + escapeHtml(I18N.changeStatus) + ' #' + escapeHtml(order.id) + '">' +
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

        function renderBars() {
            return '<div class="pl-shop__admin-metric">' +
                '<div class="pl-shop__admin-metric-label">' + escapeHtml(I18N.metricConversion) + '</div>' +
                '<div class="pl-shop__admin-bars" aria-hidden="true">' +
                '<span class="pl-shop__admin-bar-col"></span>' +
                '<span class="pl-shop__admin-bar-col"></span>' +
                '<span class="pl-shop__admin-bar-col"></span>' +
                '<span class="pl-shop__admin-bar-col pl-shop__admin-bar-col--acc"></span>' +
                '<span class="pl-shop__admin-bar-col pl-shop__admin-bar-col--acc"></span>' +
                '</div></div>';
        }

        function renderAnalyticsBars() {
            var heights = [35, 55, 42, 78, 100];
            var html = '<div class="pl-shop__admin-metric pl-shop__admin-metric--wide">' +
                '<div class="pl-shop__admin-metric-label">' + escapeHtml(I18N.metricSalesWeek) + '</div>' +
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
                renderMetric(I18N.metricOrdersToday, '47') +
                renderMetric(I18N.metricRevenue, money('84k'), 'pl-shop__admin-metric-val--acc') +
                renderBars()
            );

            var rows = '';
            state.orders.forEach(function (order, i) {
                rows += '<div class="pl-shop__admin-table-row pl-shop__admin-table-row--clickable" role="button" tabindex="0" data-admin-order="' +
                    escapeHtml(order.id) + '" style="--admin-row-i:' + i + '">' +
                    '<span class="pl-shop__admin-col-order">#' + escapeHtml(order.id) + ' · ' + escapeHtml(order.customer) + '</span>' +
                    '<span class="pl-shop__admin-col-sum">' + escapeHtml(order.sum) + '</span>' +
                    '<span class="pl-shop__admin-col-status">' + renderStatusButton(order) + '</span>' +
                    '</div>';
            });

            return metrics +
                '<div class="pl-shop__admin-table-wrap">' +
                '<div class="pl-shop__admin-table">' +
                renderTableHead([
                    { className: 'pl-shop__admin-col-order', label: I18N.colOrder },
                    { className: 'pl-shop__admin-col-sum', label: I18N.colSum },
                    { className: 'pl-shop__admin-col-status', label: I18N.colStatus }
                ]) + rows + '</div></div>';
        }

        function renderProductsView() {
            var metrics = renderMetrics(
                renderMetric(I18N.metricSku, '1 248') +
                renderMetric(I18N.metricInstock, '892', 'pl-shop__admin-metric-val--acc') +
                renderMetric(I18N.metricNewWeek, '12')
            );

            var rows = '';
            state.products.forEach(function (product, i) {
                rows += '<div class="pl-shop__admin-table-row pl-shop__admin-table-row--clickable" role="button" tabindex="0" data-admin-product="' +
                    escapeHtml(product.sku) + '" aria-label="' + escapeHtml(I18N.openProduct) + ' ' + escapeHtml(product.name) +
                    '" style="--admin-row-i:' + i + '">' +
                    '<span class="pl-shop__admin-col-order">' + escapeHtml(product.name) + '</span>' +
                    '<span class="pl-shop__admin-col-sum">' + escapeHtml(product.price) + '</span>' +
                    '<span class="pl-shop__admin-col-status pl-shop__admin-col-stock">' + escapeHtml(String(product.stock)) + ' ' + escapeHtml(I18N.unit) + '</span>' +
                    '</div>';
            });

            return metrics +
                '<div class="pl-shop__admin-table-wrap">' +
                '<div class="pl-shop__admin-table">' +
                renderTableHead([
                    { className: 'pl-shop__admin-col-order', label: I18N.colProduct },
                    { className: 'pl-shop__admin-col-sum', label: I18N.colPrice },
                    { className: 'pl-shop__admin-col-status', label: I18N.colStock }
                ]) + rows + '</div></div>';
        }

        function renderAnalyticsView() {
            var metrics = renderMetrics(
                renderMetric(I18N.metricVisitors, '2 840') +
                renderMetric(I18N.metricConversion, '3.2%', 'pl-shop__admin-metric-val--acc') +
                renderMetric(I18N.metricAvgCheck, money('1 840'))
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
                    { className: 'pl-shop__admin-col-order', label: I18N.colTop },
                    { className: 'pl-shop__admin-col-sum', label: I18N.colSales },
                    { className: 'pl-shop__admin-col-status', label: I18N.colRevenue }
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
                '<span>' + escapeHtml(I18N.together) + '</span><strong>' + escapeHtml(order.sum) + '</strong>' +
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
                '<span class="pl-shop__admin-detail-spec-label">' + escapeHtml(I18N.colPrice) + '</span>' +
                '<strong class="pl-shop__admin-detail-spec-val">' + escapeHtml(product.price) + '</strong></div>' +
                '<div class="pl-shop__admin-detail-spec" style="--admin-row-i:1">' +
                '<span class="pl-shop__admin-detail-spec-label">' + escapeHtml(I18N.colStock) + '</span>' +
                '<strong class="pl-shop__admin-detail-spec-val" data-admin-stock-val="' + escapeHtml(product.sku) + '">' +
                escapeHtml(String(product.stock)) + ' ' + escapeHtml(I18N.unit) + '</strong></div>' +
                '<div class="pl-shop__admin-detail-spec" style="--admin-row-i:2">' +
                '<span class="pl-shop__admin-detail-spec-label">' + escapeHtml(I18N.sales30Label) + '</span>' +
                '<strong class="pl-shop__admin-detail-spec-val pl-shop__admin-detail-spec-val--acc">' +
                escapeHtml(String(product.sales30)) + '</strong></div>' +
                '</div>' +
                '<p class="pl-shop__admin-detail-desc">' + escapeHtml(product.desc) + '</p>' +
                '<div class="pl-shop__admin-stock-control">' +
                '<span class="pl-shop__admin-stock-label">' + escapeHtml(I18N.updateStock) + '</span>' +
                '<div class="pl-shop__admin-stock-actions">' +
                '<button type="button" class="pl-shop__admin-stock-btn" data-admin-stock-minus="' + escapeHtml(product.sku) +
                '" aria-label="' + escapeHtml(I18N.decreaseStock) + '">−</button>' +
                '<button type="button" class="pl-shop__admin-stock-btn pl-shop__admin-stock-btn--plus" data-admin-stock-plus="' +
                escapeHtml(product.sku) + '" aria-label="' + escapeHtml(I18N.increaseStock) + '">+</button>' +
                '</div></div></div>';
        }

        function getCurrentView() {
            return historyStack[historyStack.length - 1];
        }

        function updateChrome(viewState) {
            if (viewState.view === 'order-detail') {
                titleEl.textContent = 'admin · ' + I18N.titleOrders + ' #' + viewState.id;
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
                    ? 'admin · ' + product.name
                    : 'admin · ' + I18N.titleProduct;
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
            btn.setAttribute('aria-label', I18N.changeStatus + ' #' + orderId);
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
                stockEl.textContent = product.stock + ' ' + I18N.unit;
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
