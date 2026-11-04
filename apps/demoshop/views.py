"""Публічна вітрина демо-магазину: home, каталог, товар, кошик, checkout, wishlist, NP stub."""
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import translation, timezone
from django.utils.translation import gettext as _, gettext_lazy as _lazy
from django.views.decorators.http import require_GET, require_POST

from apps.core.i18n_content import localized_text

from . import cart as cart_service
from .catalog_models import ShopCategory, ShopProduct
from .content import get_blocks_map
from .models import DemoShop
from .order_models import ShopOrder, ShopOrderItem
from .services import novaposhta as np_service
from .theme import render_theme_css

CATALOG_PAGE_SIZE = 12

CHECKOUT_CARRIERS = (
    ('packeta', _lazy('Zásilkovna / Packeta')),
    ('ppl', _lazy('PPL')),
    ('ceska_posta', _lazy('Česká pošta')),
    ('pickup', _lazy('Osobní odběr')),
)
CHECKOUT_CARRIER_LABELS = dict(CHECKOUT_CARRIERS)


def _get_active_shop(shop_slug: str) -> DemoShop:
    shop = get_object_or_404(DemoShop, slug=shop_slug, is_active=True)
    shop.blocks_map = get_blocks_map(shop)
    return shop


def _cart_count(request, shop) -> int:
    return cart_service.cart_count(request.session, shop.pk)


def _nav_categories(shop):
    return (
        ShopCategory.objects.filter(shop=shop, is_active=True, products__is_active=True)
        .distinct()
        .order_by('order')
    )


def _base_context(request, shop, **extra):
    ctx = {
        'shop': shop,
        'cart_count': _cart_count(request, shop),
        'nav_categories': _nav_categories(shop),
    }
    ctx.update(extra)
    return ctx


@require_GET
def home(request, shop_slug):
    shop = _get_active_shop(shop_slug)
    now = timezone.now()
    featured = list(
        ShopProduct.objects.filter(shop=shop, is_active=True, is_featured=True)
        .select_related('category').prefetch_related('images')[:8]
    )
    on_sale = list(
        ShopProduct.objects.filter(
            shop=shop, is_active=True, sale_end_date__gt=now, old_price__isnull=False,
        ).select_related('category').prefetch_related('images')[:8]
    )
    reviews = list(
        shop.reviews.filter(is_approved=True).select_related('product').order_by('pk')[:6]
    )
    categories = ShopCategory.objects.filter(shop=shop, is_active=True).order_by('order')
    slides = shop.hero_slides.filter(is_active=True).order_by('order')
    return render(request, 'demoshop/home.html', _base_context(
        request, shop,
        featured=featured,
        on_sale=on_sale,
        reviews=reviews,
        categories=categories,
        slides=slides,
    ))


@require_GET
def hits(request, shop_slug):
    shop = _get_active_shop(shop_slug)
    products = ShopProduct.objects.filter(shop=shop, is_active=True, is_featured=True).select_related('category').prefetch_related('images')
    return render(request, 'demoshop/hits.html', _base_context(
        request, shop, products=products,
    ))


@require_GET
def promotions(request, shop_slug):
    shop = _get_active_shop(shop_slug)
    now = timezone.now()
    products = ShopProduct.objects.filter(
        shop=shop, is_active=True, sale_end_date__gt=now, old_price__isnull=False,
    ).select_related('category').prefetch_related('images')
    return render(request, 'demoshop/promotions.html', _base_context(
        request, shop, products=products,
    ))


@require_GET
def catalog(request, shop_slug):
    shop = _get_active_shop(shop_slug)
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')
    sort = request.GET.get('sort', 'popularity')

    products = ShopProduct.objects.filter(shop=shop, is_active=True).select_related('category').prefetch_related('images')

    if query:
        products = products.filter(name__icontains=query)
    if category_slug:
        products = products.filter(category__slug=category_slug)

    if sort == 'price_asc':
        products = products.order_by('price', 'id')
    elif sort == 'price_desc':
        products = products.order_by('-price', 'id')
    elif sort == 'newest':
        products = products.order_by('-created_at', 'id')
    else:
        # popularity / default
        products = products.order_by('order', '-created_at', 'id')

    paginator = Paginator(products, CATALOG_PAGE_SIZE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = ShopCategory.objects.filter(shop=shop, is_active=True).order_by('order')
    current_category = get_object_or_404(categories, slug=category_slug) if category_slug else None

    return render(request, 'demoshop/catalog.html', _base_context(
        request, shop,
        page_obj=page_obj,
        categories=categories,
        current_category=current_category,
        query=query,
        current_sort=sort,
        total=paginator.count,
    ))


@require_GET
def product_detail(request, shop_slug, product_slug):
    shop = _get_active_shop(shop_slug)
    product = get_object_or_404(
        ShopProduct.objects.filter(shop=shop, is_active=True).select_related('category').prefetch_related('images'),
        slug=product_slug,
    )
    related = ShopProduct.objects.filter(
        shop=shop, is_active=True, category=product.category,
    ).exclude(pk=product.pk).prefetch_related('images').order_by('order')[:4]

    reviews = product.reviews.filter(is_approved=True).order_by('-created_at')

    return render(request, 'demoshop/product_detail.html', _base_context(
        request, shop,
        product=product,
        related=related,
        reviews=reviews,
    ))


@require_GET
def wishlist(request, shop_slug):
    shop = _get_active_shop(shop_slug)
    ids_str = request.GET.get('ids', '')
    ids = [int(x) for x in ids_str.split(',') if x.isdigit()]

    products = ShopProduct.objects.filter(
        shop=shop, is_active=True, pk__in=ids,
    ).select_related('category').prefetch_related('images')

    if request.headers.get('HX-Request'):
        return render(request, 'demoshop/partials/_product_grid.html', {
            'products': products,
            'shop': shop,
        })

    return render(request, 'demoshop/wishlist.html', _base_context(
        request, shop, products=products,
    ))


@require_GET
def cart_view(request, shop_slug):
    shop = _get_active_shop(shop_slug)
    lines, total = cart_service.cart_lines(request.session, shop.pk)

    if request.headers.get('HX-Request'):
        return render(request, 'demoshop/partials/_cart_lines.html', {
            'cart_lines': lines,
            'total': total,
            'shop': shop,
        })

    return render(request, 'demoshop/cart.html', _base_context(
        request, shop, cart_lines=lines, total=total,
    ))


@require_POST
def cart_add(request, shop_slug):
    shop = _get_active_shop(shop_slug)
    product_id = request.POST.get('product_id')
    qty = int(request.POST.get('qty', 1))

    product = get_object_or_404(ShopProduct, pk=product_id, shop=shop, is_active=True)
    cart_service.cart_add(request.session, shop.pk, product.pk, qty)

    response = render(request, 'demoshop/partials/_cart_confirm.html', {
        'product': product,
        'cart_count': _cart_count(request, shop),
        'shop': shop,
    })
    response['HX-Trigger'] = 'cartUpdated'
    return response


@require_POST
def cart_remove(request, shop_slug):
    shop = _get_active_shop(shop_slug)
    product_id = request.POST.get('product_id')

    cart_service.cart_remove(request.session, shop.pk, product_id)

    response = HttpResponse()
    response['HX-Trigger'] = 'cartUpdated'
    return response


@require_POST
def cart_set_qty(request, shop_slug):
    shop = _get_active_shop(shop_slug)
    product_id = request.POST.get('product_id')
    qty = int(request.POST.get('qty', 1))

    cart_service.cart_set_qty(request.session, shop.pk, product_id, qty)

    response = HttpResponse()
    response['HX-Trigger'] = 'cartUpdated'
    return response


def checkout(request, shop_slug):
    shop = _get_active_shop(shop_slug)
    lines, total = cart_service.cart_lines(request.session, shop.pk)
    if not lines:
        messages.info(request, _('Кошик порожній.'))
        return redirect('demoshop:catalog', shop_slug=shop.slug)

    if request.method == 'POST':
        # SEC-02: total always from DB prices via cart_lines
        carrier = request.POST.get('carrier', 'packeta').strip()
        if carrier not in CHECKOUT_CARRIER_LABELS:
            carrier = 'packeta'
        delivery_method = (
            ShopOrder.DeliveryMethod.ADDRESS
            if carrier == 'pickup'
            else ShopOrder.DeliveryMethod.NP_WAREHOUSE
        )
        np_city_ref = ''
        np_warehouse_ref = carrier
        lang = translation.get_language()
        city_name = request.POST.get('np_city_name', '').strip()
        warehouse_name = str(CHECKOUT_CARRIER_LABELS[carrier])
        address = request.POST.get('address', '').strip()

        order_data = {
            'shop': shop,
            'customer_name': request.POST.get('customer_name', '').strip(),
            'phone': request.POST.get('phone', '').strip(),
            'email': request.POST.get('email', '').strip(),
            'delivery_method': delivery_method,
            'np_city_ref': np_city_ref,
            'np_warehouse_ref': np_warehouse_ref,
            'total': total,
        }

        # Зберігаємо в поле поточної мови та в основне поле (UA як fallback)
        if lang == 'en':
            order_data.update({
                'np_city_name_en': city_name,
                'np_warehouse_name_en': warehouse_name,
                'address_en': address,
                'np_city_name': city_name, # fallback
            })
        elif lang == 'ru':
            order_data.update({
                'np_city_name_ru': city_name,
                'np_warehouse_name_ru': warehouse_name,
                'address_ru': address,
                'np_city_name': city_name, # fallback
            })
        elif lang == 'cs':
            order_data.update({
                'np_city_name_cs': city_name,
                'np_warehouse_name_cs': warehouse_name,
                'address_cs': address,
                'np_city_name': city_name, # fallback
            })
        else:
            order_data.update({
                'np_city_name': city_name,
                'np_warehouse_name': warehouse_name,
                'address': address,
            })

        order = ShopOrder.objects.create(**order_data)
        for line in lines:
            ShopOrderItem.objects.create(
                order=order,
                product=line['product'],
                product_name=line['product'].localized_name,
                price=line['product'].price,
                qty=line['qty'],
            )
        cart_service.clear_cart(request.session, shop.pk)
        return redirect('demoshop:order_success', shop_slug=shop.slug, order_id=order.pk)

    return render(request, 'demoshop/checkout.html', _base_context(
        request, shop, cart_lines=lines, total=total, checkout_carriers=CHECKOUT_CARRIERS,
    ))


@require_GET
def order_success(request, shop_slug, order_id):
    shop = _get_active_shop(shop_slug)
    order = get_object_or_404(ShopOrder.objects.prefetch_related('items'), pk=order_id, shop=shop)
    return render(request, 'demoshop/order_success.html', _base_context(
        request, shop, order=order,
    ))


@require_GET
def np_cities(request, shop_slug):
    _get_active_shop(shop_slug)
    q = request.GET.get('q', '')
    return JsonResponse({'results': np_service.search_cities(q)})


@require_GET
def np_warehouses(request, shop_slug):
    _get_active_shop(shop_slug)
    city_ref = request.GET.get('city_ref', '')
    return JsonResponse({'results': np_service.warehouses_for_city(city_ref)})


@require_GET
def admin_access(request, shop_slug):
    """DEPRECATED: сторінка з plaintext паролем видалена (security spec).
    
    Клієнт отримує signed КП-лінк, який видає one-time token для автологіну.
    Route залишається для backward compatibility (404).
    """
    raise Http404('Admin access page deprecated. Use signed token link.')


@require_GET
def admin_login(request, shop_slug):
    """DEPRECATED: автологін через GET заборонений (security spec).
    
    Логін тільки через POST exchange one-time token (demo_auth_views).
    Route залишається для backward compatibility (404).
    """
    raise Http404('Admin login deprecated. Use signed token exchange.')


@require_GET
def theme_css(request, shop_slug):
    shop = get_object_or_404(DemoShop, slug=shop_slug, is_active=True)
    css = render_theme_css(shop)
    response = HttpResponse(css, content_type='text/css')
    response['Cache-Control'] = 'public, max-age=300'
    return response
