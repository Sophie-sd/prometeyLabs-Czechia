"""SEO templatetags: canonical, hreflang alternates, absolute .cz URLs.

Усі абсолютні URL будуються від ``settings.CANONICAL_BASE``
(https://prometeylabs.cz), а не від request host — щоб canonical / hreflang /
og:url / JSON-LD ніколи не вказували на prometeylabs.com, onrender чи localhost.
Шлях береться з ``request.path`` без query string (?page=, ?utm_*, ?q=).
"""
from django.conf import settings
from django.template import Library
from django.urls import translate_url
from django.utils.html import format_html, format_html_join

register = Library()

DEFAULT_CANONICAL_BASE = 'https://prometeylabs.cz'


def canonical_base() -> str:
    return (getattr(settings, 'CANONICAL_BASE', '') or DEFAULT_CANONICAL_BASE).rstrip('/')


def absolute(path: str) -> str:
    """'/en/blog/' -> 'https://prometeylabs.cz/en/blog/'."""
    if not path.startswith('/'):
        path = '/' + path
    return canonical_base() + path


@register.simple_tag
def site_url(path='/'):
    """Абсолютний URL на prometeylabs.cz для довільного шляху (JSON-LD тощо)."""
    return absolute(str(path))


@register.simple_tag(takes_context=True)
def canonical_url(context):
    """Self-canonical: https://prometeylabs.cz + request.path (без query)."""
    request = context.get('request')
    if request is None:
        return ''
    return absolute(request.path)


@register.simple_tag(takes_context=True)
def canonical_link(context):
    url = canonical_url(context)
    if not url:
        return ''
    return format_html('<link rel="canonical" href="{}">', url)


@register.simple_tag(takes_context=True)
def hreflang_links(context):
    """Рендерить <link rel="alternate" hreflang="..."> для всіх LANGUAGES + x-default.

    Self-referencing (поточна сторінка теж включається — вимога Google),
    взаємні пари cs/en, тільки домен prometeylabs.cz.
    x-default → verze v LANGUAGE_CODE (cs, bez prefixu).
    Якщо жодна альтернативна URL не резолвиться (сторінка поза i18n_patterns,
    напр. /admin/, або 404) — тег нічого не рендерить.
    """
    request = context.get('request')
    if request is None:
        return ''

    current_path = request.path
    entries = []
    seen_urls = set()

    for lang_code, _label in settings.LANGUAGES:
        absolute_url = absolute(translate_url(current_path, lang_code))
        if absolute_url in seen_urls:
            continue
        seen_urls.add(absolute_url)
        entries.append((lang_code, absolute_url))

    # Якщо всі мови звелись до однієї й тієї ж URL — сторінка не мультимовна
    # (напр. поза i18n_patterns), hreflang тут не потрібен.
    if len(entries) <= 1:
        return ''

    entries.append(('x-default', absolute(translate_url(current_path, settings.LANGUAGE_CODE))))

    return format_html_join(
        '\n    ',
        '<link rel="alternate" hreflang="{}" href="{}">',
        entries,
    )
