"""First-party cookie consent: banner texts (cs/en) + consent audit endpoint.

Banner markup: templates/partials/consent_banner.html
Consent Mode v2 default + GTM gating: templates/partials/gtm_head.html
"""
import json
import re

from django.http import JsonResponse
from django.utils.translation import get_language
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

CONSENT_VERSION = 1

CONSENT_TEXTS = {
    'cs': {
        'title': 'Cookies a soukromí',
        'text': ('Nezbytné cookies potřebujeme pro chod webu. Analytické (Google Analytics) '
                 'a marketingové cookies (Google Ads – měření konverzí, personalizace reklam) '
                 'použijeme jen s vaším souhlasem. Souhlas můžete kdykoli odvolat přes '
                 '„Nastavení cookies“ v zápatí.'),
        'cookies_link': 'Zásady cookies',
        'privacy_link': 'Ochrana osobních údajů',
        'google_link': 'Jak Google používá data',
        'accept': 'Přijmout vše',
        'reject': 'Odmítnout vše',
        'settings': 'Nastavení',
        'save': 'Uložit výběr',
        'necessary': 'Nezbytné',
        'necessary_desc': 'Chod webu, zabezpečení formulářů, uložení vaší volby. Vždy aktivní.',
        'always': 'Vždy aktivní',
        'analytics': 'Analytické',
        'analytics_desc': 'Google Analytics 4 – anonymní statistiky návštěvnosti.',
        'marketing': 'Marketingové',
        'marketing_desc': 'Google Ads – měření konverzí, remarketing a personalizace reklam.',
        'aria': 'Souhlas s cookies',
    },
    'en': {
        'title': 'Cookies & privacy',
        'text': ('We need necessary cookies to run the site. Analytics (Google Analytics) and '
                 'marketing cookies (Google Ads – conversion measurement, ad personalisation) '
                 'are used only with your consent. You can withdraw consent at any time via '
                 '“Cookie settings” in the footer.'),
        'cookies_link': 'Cookie Policy',
        'privacy_link': 'Privacy Policy',
        'google_link': 'How Google uses data',
        'accept': 'Accept all',
        'reject': 'Reject all',
        'settings': 'Settings',
        'save': 'Save choice',
        'necessary': 'Necessary',
        'necessary_desc': 'Site operation, form security, storing your choice. Always on.',
        'always': 'Always on',
        'analytics': 'Analytics',
        'analytics_desc': 'Google Analytics 4 – anonymous traffic statistics.',
        'marketing': 'Marketing',
        'marketing_desc': 'Google Ads – conversion measurement, remarketing and ad personalisation.',
        'aria': 'Cookie consent',
    },
}


def consent_texts(lang=None):
    lang = (lang or get_language() or 'cs').split('-')[0]
    return CONSENT_TEXTS['en'] if lang == 'en' else CONSENT_TEXTS['cs']


_ID_RE = re.compile(r'^[a-f0-9]{16,40}$')
_ACTIONS = {'accept_all', 'reject_all', 'custom', 'migrated'}


@csrf_exempt  # anonymous beacon, no session/state change; strictly validated below
@require_POST
def consent_log(request):
    from .consent_models import ConsentLog

    if len(request.body or b'') > 1024:
        return JsonResponse({'ok': False}, status=413)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({'ok': False}, status=400)
    if not isinstance(data, dict):
        return JsonResponse({'ok': False}, status=400)
    cid = str(data.get('id') or '')
    action = str(data.get('action') or '')
    if not _ID_RE.match(cid) or action not in _ACTIONS:
        return JsonResponse({'ok': False}, status=400)
    ConsentLog.objects.create(
        consent_id=cid,
        action=action,
        analytics=bool(data.get('a')),
        marketing=bool(data.get('m')),
        policy_version=CONSENT_VERSION,
        language=str(data.get('lang') or '')[:8],
        path=str(data.get('path') or '')[:200],
        user_agent=(request.META.get('HTTP_USER_AGENT') or '')[:200],
    )
    return JsonResponse({'ok': True})
