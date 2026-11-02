"""POST currency switch. No HTMX in this fork: set the cookie and reload the page."""
from django.conf import settings
from django.http import HttpResponseRedirect
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from apps.core.fx import CURRENCY_COOKIE, CURRENCY_COOKIE_AGE, normalize_currency
from apps.core.i18n_views import _redirect_target


@never_cache
@require_POST
def set_currency(request):
    code = normalize_currency(request.POST.get('currency'))
    response = HttpResponseRedirect(_redirect_target(request, request.POST.get('next')) or '/')
    response.set_cookie(
        CURRENCY_COOKIE,
        code,
        max_age=CURRENCY_COOKIE_AGE,
        path=getattr(settings, 'LANGUAGE_COOKIE_PATH', '/') or '/',
        domain=getattr(settings, 'LANGUAGE_COOKIE_DOMAIN', None),
        secure=getattr(settings, 'LANGUAGE_COOKIE_SECURE', False),
        httponly=True,
        samesite=getattr(settings, 'LANGUAGE_COOKIE_SAMESITE', 'Lax') or 'Lax',
    )
    return response
