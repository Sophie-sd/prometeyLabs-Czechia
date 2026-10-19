"""Генерація PDF «Базове ТЗ для сайту» через xhtml2pdf."""
from __future__ import annotations

import io
from datetime import timezone as dt_timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.template.loader import render_to_string
from django.utils import translation
from django.utils import timezone
from zoneinfo import ZoneInfo

# Дата в PDF — місцевий час CZ (created_at зберігається в UTC). #57
TZ_PDF_TIMEZONE = ZoneInfo('Europe/Prague')


def format_tz_created(created_at) -> str:
    if created_at is None:
        return ''
    if timezone.is_naive(created_at):
        created_at = timezone.make_aware(created_at, dt_timezone.utc)
    return timezone.localtime(created_at, TZ_PDF_TIMEZONE).strftime('%d.%m.%Y %H:%M')


# Мапінг ключів квіза → людські формулювання (uk / en / cs / ru)
LABELS = {
    'uk': {
        'site_type': 'Тип сайту',
        'goals': 'Цілі проєкту',
        'sections': 'Необхідні розділи',
        'features': 'Функціонал',
        'style': 'Стиль і візуал',
        'timeline': 'Терміни',
        'budget': 'Орієнтовний бюджет',
        'description': 'Опис від клієнта',
        'extra': 'Додаткові побажання',
        'title': 'Базове технічне завдання на розробку сайту',
        'intro': (
            'Документ сформовано автоматично за відповідями клієнта. '
            'Розширене ТЗ з деталізацією сценаріїв, структури сторінок '
            'та технічних вимог надійде на email протягом доби.'
        ),
        'site_types': {
            'landing': 'Лендінг / промо-сайт',
            'corporate': 'Корпоративний сайт',
            'shop': 'Інтернет-магазин',
            'portal': 'Портал / веб-сервіс',
            'other': 'Інший тип',
        },
        'goal_map': {
            'leads': 'Збір заявок і лідів',
            'sales': 'Продажі онлайн',
            'brand': 'Презентація бренду',
            'info': 'Інформаційний ресурс',
            'support': 'Підтримка клієнтів',
        },
        'section_map': {
            'home': 'Головна',
            'about': 'Про компанію',
            'services': 'Послуги / товари',
            'portfolio': 'Портфоліо / кейси',
            'blog': 'Блог / новини',
            'contacts': 'Контакти',
            'faq': 'FAQ',
            'cabinet': 'Особистий кабінет',
        },
        'feature_map': {
            'crm': 'Інтеграція з CRM',
            'payment': 'Оплата онлайн',
            'multilang': 'Мультимовність',
            'seo': 'SEO-оптимізація',
            'ads': 'Підготовка під рекламу',
            'chat': 'Чат / месенджери',
            'analytics': 'Аналітика і цілі',
            'admin': 'Зручна адмінка',
        },
        'style_map': {
            'minimal': 'Мінімалізм',
            'premium': 'Преміум / luxury',
            'bold': 'Яскравий / сміливий',
            'corporate': 'Строгий корпоративний',
            'creative': 'Креативний',
        },
        'timeline_map': {
            'asap': 'Якнайшвидше (до 2 тижнів)',
            'month': 'До 1 місяця',
            'quarter': '1–3 місяці',
            'flex': 'Гнучкий графік',
        },
        'budget_map': {
            'starter': 'До 50 000 грн',
            'growth': '50–150 000 грн',
            'pro': '150–400 000 грн',
            'enterprise': 'Від 400 000 грн',
            'unknown': 'Потрібна консультація',
        },
    },
    'en': {
        'site_type': 'Website type',
        'goals': 'Project goals',
        'sections': 'Required sections',
        'features': 'Features',
        'style': 'Visual style',
        'timeline': 'Timeline',
        'budget': 'Estimated budget',
        'description': 'Client description',
        'extra': 'Extra notes',
        'title': 'Basic website brief',
        'intro': (
            'This document was generated automatically from the client\'s quiz answers. '
            'An extended brief with detailed scenarios, page structure and technical '
            'requirements will be sent by email within 24 hours.'
        ),
        'site_types': {
            'landing': 'Landing page / promo site',
            'corporate': 'Corporate website',
            'shop': 'E-commerce store',
            'portal': 'Portal / web service',
            'other': 'Other type',
        },
        'goal_map': {
            'leads': 'Lead generation',
            'sales': 'Online sales',
            'brand': 'Brand presentation',
            'info': 'Information resource',
            'support': 'Customer support',
        },
        'section_map': {
            'home': 'Home',
            'about': 'About',
            'services': 'Services / products',
            'portfolio': 'Portfolio / cases',
            'blog': 'Blog / news',
            'contacts': 'Contacts',
            'faq': 'FAQ',
            'cabinet': 'Client area',
        },
        'feature_map': {
            'crm': 'CRM integration',
            'payment': 'Online payments',
            'multilang': 'Multilingual',
            'seo': 'SEO optimization',
            'ads': 'Ads-ready setup',
            'chat': 'Chat / messengers',
            'analytics': 'Analytics & goals',
            'admin': 'Easy admin panel',
        },
        'style_map': {
            'minimal': 'Minimal',
            'premium': 'Premium / luxury',
            'bold': 'Bold / vibrant',
            'corporate': 'Strict corporate',
            'creative': 'Creative',
        },
        'timeline_map': {
            'asap': 'ASAP (within 2 weeks)',
            'month': 'Within 1 month',
            'quarter': '1–3 months',
            'flex': 'Flexible schedule',
        },
        'budget_map': {
            'starter': 'Up to €1,200',
            'growth': '€1,200–3,500',
            'pro': '€3,500–10,000',
            'enterprise': '€10,000+',
            'unknown': 'Need a consultation',
        },
    },
    'cs': {
        'site_type': 'Typ webu',
        'goals': 'Cíle projektu',
        'sections': 'Potřebné sekce',
        'features': 'Funkce',
        'style': 'Styl a vizuál',
        'timeline': 'Termín',
        'budget': 'Orientační rozpočet',
        'description': 'Popis od klienta',
        'extra': 'Další přání',
        'title': 'Základní zadání pro tvorbu webu',
        'intro': (
            'Dokument byl vytvořen automaticky podle odpovědí klienta. '
            'Rozšířené zadání s podrobnými scénáři, strukturou stránek '
            'a technickými požadavky vám pošleme e-mailem do 24 hodin.'
        ),
        'site_types': {
            'landing': 'Landing page / promo web',
            'corporate': 'Firemní web',
            'shop': 'E-shop',
            'portal': 'Portál / webová služba',
            'other': 'Jiný typ',
        },
        'goal_map': {
            'leads': 'Sběr poptávek a leadů',
            'sales': 'Online prodej',
            'brand': 'Prezentace značky',
            'info': 'Informační zdroj',
            'support': 'Podpora klientů',
        },
        'section_map': {
            'home': 'Domů',
            'about': 'O firmě',
            'services': 'Služby / produkty',
            'portfolio': 'Portfolio / případové studie',
            'blog': 'Blog / novinky',
            'contacts': 'Kontakty',
            'faq': 'FAQ',
            'cabinet': 'Osobní účet',
        },
        'feature_map': {
            'crm': 'Integrace s CRM',
            'payment': 'Online platba',
            'multilang': 'Vícejazyčnost',
            'seo': 'SEO optimalizace',
            'ads': 'Příprava na reklamu',
            'chat': 'Chat / messengery',
            'analytics': 'Analytika a cíle',
            'admin': 'Přehledná administrace',
        },
        'style_map': {
            'minimal': 'Minimalismus',
            'premium': 'Prémiový / luxusní',
            'bold': 'Výrazný / odvážný',
            'corporate': 'Striktně firemní',
            'creative': 'Kreativní',
        },
        'timeline_map': {
            'asap': 'Co nejdříve (do 2 týdnů)',
            'month': 'Do 1 měsíce',
            'quarter': '1–3 měsíce',
            'flex': 'Flexibilní termín',
        },
        'budget_map': {
            'starter': 'Do 30 000 Kč',
            'growth': '30 000–80 000 Kč',
            'pro': '80 000–200 000 Kč',
            'enterprise': 'Od 200 000 Kč',
            'unknown': 'Potřebuji konzultaci',
        },
    },
    'ru': {
        'site_type': 'Тип сайта',
        'goals': 'Цели проекта',
        'sections': 'Необходимые разделы',
        'features': 'Функционал',
        'style': 'Стиль и визуал',
        'timeline': 'Сроки',
        'budget': 'Ориентировочный бюджет',
        'description': 'Описание от клиента',
        'extra': 'Дополнительные пожелания',
        'title': 'Базовое техническое задание на разработку сайта',
        'intro': (
            'Документ сформирован автоматически по ответам клиента. '
            'Расширенное ТЗ со структурой страниц и техническими требованиями '
            'придёт на email в течение суток.'
        ),
        'site_types': {
            'landing': 'Лендинг / промо-сайт',
            'corporate': 'Корпоративный сайт',
            'shop': 'Интернет-магазин',
            'portal': 'Портал / веб-сервис',
            'other': 'Другой тип',
        },
        'goal_map': {
            'leads': 'Сбор заявок и лидов',
            'sales': 'Онлайн-продажи',
            'brand': 'Презентация бренда',
            'info': 'Информационный ресурс',
            'support': 'Поддержка клиентов',
        },
        'section_map': {
            'home': 'Главная',
            'about': 'О компании',
            'services': 'Услуги / товары',
            'portfolio': 'Портфолио / кейсы',
            'blog': 'Блог / новости',
            'contacts': 'Контакты',
            'faq': 'FAQ',
            'cabinet': 'Личный кабинет',
        },
        'feature_map': {
            'crm': 'Интеграция с CRM',
            'payment': 'Онлайн-оплата',
            'multilang': 'Мультиязычность',
            'seo': 'SEO-оптимизация',
            'ads': 'Подготовка под рекламу',
            'chat': 'Чат / мессенджеры',
            'analytics': 'Аналитика и цели',
            'admin': 'Удобная админка',
        },
        'style_map': {
            'minimal': 'Минимализм',
            'premium': 'Премиум / luxury',
            'bold': 'Яркий / смелый',
            'corporate': 'Строгий корпоративный',
            'creative': 'Креативный',
        },
        'timeline_map': {
            'asap': 'Как можно скорее (до 2 недель)',
            'month': 'До 1 месяца',
            'quarter': '1–3 месяца',
            'flex': 'Гибкий график',
        },
        'budget_map': {
            'starter': 'До 50 000 грн',
            'growth': '50–150 000 грн',
            'pro': '150–400 000 грн',
            'enterprise': 'От 400 000 грн',
            'unknown': 'Нужна консультация',
        },
    },
}


def _static_path(relative: str) -> Optional[Path]:
    found = find(relative)
    if found:
        return Path(found).resolve()
    fallback = Path(settings.BASE_DIR) / 'static' / relative
    if fallback.exists():
        return fallback.resolve()
    return None


def _font_paths() -> Dict[str, str]:
    regular = _static_path('fonts/NotoSans-Regular.ttf')
    bold = _static_path('fonts/NotoSans-Bold.ttf')
    return {
        'regular': str(regular) if regular else '',
        'bold': str(bold) if bold else '',
    }


def _map_list(keys: Any, mapping: Dict[str, str]) -> List[str]:
    if isinstance(keys, str):
        keys = [keys]
    if not isinstance(keys, list):
        return []
    out = []
    for key in keys:
        label = mapping.get(str(key))
        if label:
            out.append(label)
        elif key:
            out.append(str(key))
    return out


def build_tz_context(submission) -> dict:
    lang = (translation.get_language() or 'cs').split('-')[0].lower()
    if lang not in LABELS:
        lang = 'cs'
    L = LABELS[lang]
    quiz = (submission.extra_data or {}).get('quiz') or {}

    sections: List[Dict[str, str]] = []

    site_type = quiz.get('site_type')
    if site_type:
        sections.append({
            'title': L['site_type'],
            'body': L['site_types'].get(str(site_type), str(site_type)),
        })

    goals = _map_list(quiz.get('goals'), L['goal_map'])
    if goals:
        sections.append({'title': L['goals'], 'body': ' · '.join(goals)})

    secs = _map_list(quiz.get('sections'), L['section_map'])
    if secs:
        sections.append({'title': L['sections'], 'body': ' · '.join(secs)})

    feats = _map_list(quiz.get('features'), L['feature_map'])
    if feats:
        sections.append({'title': L['features'], 'body': ' · '.join(feats)})

    style = quiz.get('style')
    if style:
        sections.append({
            'title': L['style'],
            'body': L['style_map'].get(str(style), str(style)),
        })

    timeline = quiz.get('timeline')
    if timeline:
        sections.append({
            'title': L['timeline'],
            'body': L['timeline_map'].get(str(timeline), str(timeline)),
        })

    budget = quiz.get('budget')
    if budget:
        sections.append({
            'title': L['budget'],
            'body': L['budget_map'].get(str(budget), str(budget)),
        })

    if quiz.get('description'):
        sections.append({
            'title': L['description'],
            'body': str(quiz['description'])[:2000],
        })
    if quiz.get('extra'):
        sections.append({
            'title': L['extra'],
            'body': str(quiz['extra'])[:1000],
        })

    fonts = _font_paths()
    return {
        'title': L['title'],
        'intro': L['intro'],
        'sections': sections,
        'client_name': submission.name,
        'client_email': submission.email,
        'client_phone': submission.phone,
        'created': format_tz_created(submission.created_at),
        'font_regular': fonts['regular'],
        'font_bold': fonts['bold'],
        'lang': lang,
    }


def _link_callback(uri, rel):
    if uri.startswith('file://'):
        return uri.replace('file://', '')
    if uri.startswith('/'):
        return uri
    static_candidate = Path(settings.BASE_DIR) / 'static' / uri
    if static_candidate.exists():
        return str(static_candidate)
    found = find(uri)
    if found:
        return found
    return uri


def generate_tz_pdf_bytes(submission) -> bytes:
    from xhtml2pdf import pisa

    html = render_to_string('pdf/tz_document.html', build_tz_context(submission))
    result = io.BytesIO()
    pdf = pisa.CreatePDF(
        src=io.BytesIO(html.encode('utf-8')),
        dest=result,
        encoding='utf-8',
        link_callback=_link_callback,
    )
    if pdf.err:
        raise RuntimeError(f'TZ PDF failed with {pdf.err} error(s)')
    return result.getvalue()
