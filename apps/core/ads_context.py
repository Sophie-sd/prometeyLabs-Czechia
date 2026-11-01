"""Context for ads landings: copy + breadcrumbs + JSON-LD from one source."""
from pathlib import Path

from django.conf import settings
from django.templatetags.static import static
from django.urls import reverse
from django.utils import translation

from .ads_copy import (
    SITE,
    SHOP_SLUGS,
    contacts_copy,
    corp_copy,
    crumbs_copy,
    faq_pairs,
    lang,
    process_site_copy,
    rs_copy,
    shop_copy,
)
from .ads_copy_dorobka import dorobka_copy
from .ads_schema import hreflang_urls, schema_scripts
from .mixins import published_portfolio_queryset


def _abs(path):
    return SITE + path


def _reverse(name, language):
    with translation.override(language):
        return reverse(name)


def hreflang_for(name):
    return hreflang_urls(_reverse(name, 'cs'), _reverse(name, 'en'))


def _crumbs(last_name, last_url):
    labels = crumbs_copy()
    return [
        {'name': labels['home'], 'url': _abs(_reverse('home', lang()))},
        {'name': labels['services'], 'url': ''},
        {'name': last_name, 'url': last_url},
    ]


ADS_CARD_DIR = 'images/portfolio/screens/ads-cards'
ADS_CARD_WIDTHS = (400, 800)


def _ads_card_images(slug):
    """Top-crop 280:180 thumbs. Empty when not generated, so the card keeps the portfolio image."""
    rels = [f'{ADS_CARD_DIR}/{slug}-{width}w.webp' for width in ADS_CARD_WIDTHS]
    base = Path(settings.BASE_DIR) / 'static'
    if not all((base / rel).is_file() for rel in rels):
        return '', ''
    srcset = ', '.join(f'{static(rel)} {width}w' for rel, width in zip(rels, ADS_CARD_WIDTHS))
    return static(rels[-1]), srcset


def shop_portfolio_projects():
    found = {
        project.slug: project
        for project in published_portfolio_queryset().filter(slug__in=SHOP_SLUGS)
    }
    projects = [found[slug] for slug in SHOP_SLUGS if slug in found]
    for project in projects:
        project.ads_card_src, project.ads_card_srcset = _ads_card_images(project.slug)
    return projects


def shop_ads_context():
    seo = hreflang_for('internet_shop_v2')
    copy = shop_copy()
    faq = faq_pairs(copy['faq'])
    crumbs = _crumbs(copy['crumb'], seo['canonical'])
    process = process_site_copy()
    return {
        'ads_tz': True,
        'ads_copy': copy,
        'ads_faq': faq,
        'ads_contacts': contacts_copy(),
        'ads_crumbs': crumbs,
        'ads_seo': seo,
        'ads_process': process,
        'ads_json_ld': schema_scripts(crumbs, faq),
        'shop_portfolio': shop_portfolio_projects(),
        'page_title': copy['title'],
        'meta_description': copy['description'],
        'og_title': copy['title'],
    }


def rs_ads_context():
    seo = hreflang_for('rozrobka_sajtiv')
    copy = rs_copy()
    faq = faq_pairs(copy['faq'])
    crumbs = _crumbs(copy['crumb'], seo['canonical'])
    return {
        'ads_tz': True,
        'ads_copy': copy,
        'ads_faq': faq,
        'ads_contacts': contacts_copy(),
        'ads_crumbs': crumbs,
        'ads_seo': seo,
        'ads_process': process_site_copy(),
        'ads_json_ld': schema_scripts(crumbs, faq),
        'page_title': copy['title'],
        'meta_description': copy['description'],
        'og_title': copy['title'],
    }


def dorobka_ads_context():
    copy = dorobka_copy()
    seo = hreflang_for('dorobka_sajtu')
    faq = faq_pairs(copy['faq'])
    crumbs = _crumbs(copy['crumb'], seo['canonical'])
    return {
        'ads_copy': copy,
        'ads_faq': faq,
        'ads_contacts': contacts_copy(),
        'ads_crumbs': crumbs,
        'ads_seo': seo,
        'ads_json_ld': schema_scripts(crumbs, faq),
        'page_title': copy['title'],
        'meta_description': copy['description'],
        'og_title': copy['title'],
        'hide_developer_modal': True,
        'hide_lang_suggest': True,
    }


def corporate_ads_context():
    seo = hreflang_for('corporate_website_v2')
    last = 'Firemní weby a landingy' if lang() == 'cs' else 'Corporate websites and landing pages'
    crumbs = _crumbs(last, seo['canonical'])
    copy = corp_copy()
    faq = faq_pairs(copy['faq'])
    return {
        'ads_copy': copy,
        'ads_faq': faq,
        'ads_crumbs': crumbs,
        'ads_seo': seo,
        'ads_contacts': contacts_copy(),
        'ads_json_ld': schema_scripts(crumbs, faq),
    }


def home_hreflang_context():
    return {'ads_seo': hreflang_for('home')}
