"""Views для signed-token автологіну у DemoAdminSite.

Security spec: two-level tokens
1. КП-лінк /demo/<slug>/open/<kp_token> (довгий TTL = термін демо)
2. One-time token (TTL 60-120s, jti в БД, consumed атомарно)
"""
import secrets
from datetime import timedelta

from django.contrib.auth import login as auth_login
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET, require_POST

from .models import DemoLoginToken, DemoShop

# TTL для one-time токену (60-120s)
ONE_TIME_TOKEN_TTL_SECONDS = 90

# Salt для підпису (окремий від інших signing операцій)
DEMO_LOGIN_SALT = 'demo-admin-login.v1'


def _get_client_ip(request):
    """Отримати IP клієнта з урахуванням proxy."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def _create_one_time_token(demo_shop: DemoShop, request) -> tuple[str, str]:
    """Створює one-time token з jti в БД.
    
    Returns:
        (signed_token, jti)
    """
    jti = secrets.token_urlsafe(32)
    
    # Зберігаємо jti в БД (used_at=None, consumed пізніше)
    DemoLoginToken.objects.create(
        jti=jti,
        demo_shop=demo_shop,
        ip_address=_get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:300],
    )
    
    # Підписуємо jti з timestamp
    signer = TimestampSigner(salt=DEMO_LOGIN_SALT)
    signed_token = signer.sign(jti)
    
    return signed_token, jti


def _consume_one_time_token(signed_token: str, demo_shop: DemoShop) -> bool:
    """Перевіряє і consumed one-time token атомарно.
    
    Returns:
        True якщо токен валідний і не використаний, False інакше
    """
    try:
        # Перевіряємо підпис і TTL
        signer = TimestampSigner(salt=DEMO_LOGIN_SALT)
        jti_raw = signer.unsign(signed_token, max_age=ONE_TIME_TOKEN_TTL_SECONDS)
        # unsign може повертати bytes або str, нормалізуємо до str
        jti = jti_raw.decode('utf-8') if isinstance(jti_raw, bytes) else str(jti_raw)
    except (BadSignature, SignatureExpired):
        return False
    
    # Атомарно consumed токен (UPDATE WHERE used_at IS NULL)
    now = timezone.now()
    updated = DemoLoginToken.objects.filter(
        jti=jti,
        demo_shop=demo_shop,
        used_at__isnull=True,
    ).update(used_at=now)
    
    return updated > 0


@never_cache
@require_GET
def demo_open_link(request, shop_slug, kp_token):
    """КП-лінк: /demo/<slug>/open/<kp_token>
    
    Перевіряє kp_token (довгий TTL), створює та consumed one-time token,
    виконує автологін і редірект на /demo-admin/ — все в одному запиті.
    
    Токен ніколи не з'являється в URL.
    """
    import json
    
    # Перевіряємо що demo існує і активне
    demo_shop = get_object_or_404(DemoShop, slug=shop_slug, is_active=True)
    
    # Перевіряємо kp_token signature (довгий TTL = 90 днів)
    try:
        signer = TimestampSigner(salt=f'{DEMO_LOGIN_SALT}:kp')
        unsigned = signer.unsign(kp_token, max_age=90 * 86400)  # 90 днів
        payload = json.loads(unsigned)
        
        # Перевіряємо що токен для цього demo
        if payload.get('demo_id') != demo_shop.pk:
            raise Http404('Token mismatch')
    except (BadSignature, SignatureExpired, json.JSONDecodeError, KeyError):
        raise Http404('Invalid or expired KP token')
    
    # Створюємо і одразу consumed one-time token (server-side exchange)
    one_time_token, jti = _create_one_time_token(demo_shop, request)
    
    if not _consume_one_time_token(one_time_token, demo_shop):
        raise Http404('Failed to consume token')
    
    # Логінимо demo owner user
    if not demo_shop.owner_user or not demo_shop.owner_user.is_active:
        raise Http404('Demo user not found or inactive')
    
    user = demo_shop.owner_user
    
    # Django login (робить cycle_key автоматично)
    auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    
    # Встановлюємо demo_scope у сесії
    request.session['demo_scope'] = {
        'type': 'demoshop',
        'id': demo_shop.pk,
    }
    
    # Expiry <= 8 годин (має бути ПІСЛЯ auth_login)
    request.session.set_expiry(8 * 3600)
    # Мова demo admin з КП (cs за замовчуванням, en з /en/ КП)
    from apps.core.middleware import DEMO_ADMIN_LANG_SESSION_KEY, DEMO_ADMIN_LANGUAGES
    lang = request.GET.get('lang')
    request.session[DEMO_ADMIN_LANG_SESSION_KEY] = lang if lang in DEMO_ADMIN_LANGUAGES else 'cs'
    request.session.modified = True
    
    # Редірект на demo admin без токену в URL
    response = redirect(f'/demo-admin/{shop_slug}/')
    
    # Security headers
    response['Referrer-Policy'] = 'no-referrer'
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
    response['X-Robots-Tag'] = 'noindex, nofollow'
    
    return response


@never_cache
@csrf_protect
@require_POST
def demo_token_exchange(request, shop_slug):
    """Обмін one-time token на автологін.
    
    POST /demo-admin/<slug>/exchange/
    Body: one_time_token
    
    Consumed token, логінить юзера, встановлює session demo_scope,
    редірект на /demo-admin/<slug>/ без токену в URL.
    """
    demo_shop = get_object_or_404(DemoShop, slug=shop_slug, is_active=True)
    
    one_time_token = request.POST.get('one_time_token', '')
    
    if not _consume_one_time_token(one_time_token, demo_shop):
        raise Http404('Invalid or expired token')
    
    # Логінимо demo owner user
    if not demo_shop.owner_user or not demo_shop.owner_user.is_active:
        raise Http404('Demo user not found or inactive')
    
    user = demo_shop.owner_user
    
    # Django login (робить cycle_key автоматично)
    auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    
    # Встановлюємо demo_scope у сесії
    request.session['demo_scope'] = {
        'type': 'demoshop',
        'id': demo_shop.pk,
    }
    
    # Expiry <= 8 годин (має бути ПІСЛЯ auth_login)
    request.session.set_expiry(8 * 3600)
    request.session.modified = True
    
    # Редірект на demo admin без токену в URL
    return redirect(f'/demo-admin/{shop_slug}/')


@never_cache
@require_GET
def demo_admin_index(request, shop_slug):
    """Landing page /demo-admin/<slug>/
    
    Перевіряє права і редірект на фактичну admin index.
    """
    from .demo_admin_site import demo_admin_site
    
    demo_shop = get_object_or_404(DemoShop, slug=shop_slug, is_active=True)
    
    if not demo_admin_site.has_permission(request):
        return redirect('/')
    
    # Редірект на фактичну admin index
    return redirect('/demo-admin/')
