"""JSON-LD builders for ads landings. FAQ text comes from the same Python lists as the visible FAQ."""
import json

from django.conf import settings
from django.utils.safestring import mark_safe

from .ads_copy import SITE, lang
from .utils import SITE_CONTACT_DEFAULTS, get_site_contact_settings

LOCALITY = {'cs': 'Praha', 'en': 'Prague'}


def dumps(obj):
    return mark_safe(json.dumps(obj, ensure_ascii=False, separators=(',', ':')))


def breadcrumb_ld(items):
    """Google requires `item` on every ListItem except the last; crumbs without a URL
    (e.g. the unlinked "Services" label) stay visible but are left out of JSON-LD."""
    linked = [item for item in items if item.get('url')]
    elements = [
        {
            '@type': 'ListItem',
            'position': index,
            'name': item['name'],
            'item': item['url'],
        }
        for index, item in enumerate(linked, start=1)
    ]
    return {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': elements,
    }


def faq_ld(pairs):
    return {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': [
            {
                '@type': 'Question',
                'name': item['q'],
                'acceptedAnswer': {'@type': 'Answer', 'text': item['a']},
            }
            for item in pairs
        ],
    }


def _same_as(contact):
    urls = []
    for attr, fallback in (
        ('instagram_url', SITE_CONTACT_DEFAULTS['instagram_url']),
        ('facebook_url', SITE_CONTACT_DEFAULTS['facebook_url']),
        ('linkedin_url', SITE_CONTACT_DEFAULTS['linkedin_url']),
        ('tiktok_url', SITE_CONTACT_DEFAULTS['tiktok_url']),
        ('telegram_url', SITE_CONTACT_DEFAULTS['telegram_url']),
    ):
        value = (getattr(contact, attr, None) or fallback or '').strip()
        if value:
            urls.append(value)
    return urls


def organization_ld():
    contact = get_site_contact_settings()
    code = lang()
    email = (getattr(contact, 'email', None) or SITE_CONTACT_DEFAULTS['email']).strip()
    address_line = (
        getattr(contact, 'czechia_address_en' if code == 'en' else 'czechia_address_cs', None)
        or SITE_CONTACT_DEFAULTS['czechia_address_en' if code == 'en' else 'czechia_address_cs']
    )
    org = {
        '@context': 'https://schema.org',
        '@type': ['Organization', 'ProfessionalService'],
        'name': 'PrometeyLabs',
        'url': SITE + '/',
        'email': email,
        'address': {
            '@type': 'PostalAddress',
            'streetAddress': address_line,
            'addressLocality': LOCALITY.get(code, 'Prague'),
            'addressCountry': 'CZ',
        },
        'sameAs': _same_as(contact),
    }
    phone = (getattr(contact, 'phone_e164', None) or '').strip()
    if phone:
        org['telephone'] = phone
    return org


def hreflang_urls(cs_path, en_path):
    cs = SITE + cs_path
    en = SITE + en_path
    current = en if lang() == 'en' else cs
    return {
        'canonical': current,
        'cs': cs,
        'en': en,
        'x_default': cs,
    }


def schema_scripts(breadcrumbs, faq_pairs=None):
    blocks = [dumps(breadcrumb_ld(breadcrumbs)), dumps(organization_ld())]
    if faq_pairs:
        blocks.append(dumps(faq_ld(faq_pairs)))
    return blocks
