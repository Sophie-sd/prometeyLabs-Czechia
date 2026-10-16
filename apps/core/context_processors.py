"""
Context processors для глобальних змінних шаблонів
"""
from django.conf import settings
from django.utils.translation import get_language

from apps.core.utils import get_site_contact_settings


def global_settings(request):
    """
    Додає глобальні налаштування до контексту всіх шаблонів.
    `csp_nonce` — per-request nonce, set by CSPMiddleware.
    """
    lang = (get_language() or 'uk').split('-')[0]
    if lang in ('cs', 'en'):
        # Czech site: +420 default for both public languages (mask stays editable)
        phone_placeholder = '+420'
    else:
        phone_placeholder = '+38(___)__-__-___'
    return {
        'FACEBOOK_PIXEL_ID': getattr(settings, 'FACEBOOK_PIXEL_ID', None),
        'COOKIEYES_ID': getattr(settings, 'COOKIEYES_ID', '') or '',
        'DEBUG': settings.DEBUG,
        'csp_nonce': getattr(request, 'csp_nonce', ''),
        'site_contact': get_site_contact_settings(),
        'phone_placeholder': phone_placeholder,
    }

