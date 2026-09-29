"""SEO templatetags: hreflang alternate links для мультимовних сторінок."""
from django.conf import settings
from django.template import Library
from django.urls import translate_url
from django.utils.html import format_html_join

register = Library()


@register.simple_tag(takes_context=True)
def hreflang_links(context):
    """Рендерить <link rel="alternate" hreflang="..."> для всіх LANGUAGES + x-default.

    Self-referencing (поточна сторінка теж включається — вимога Google).
    x-default → verze v LANGUAGE_CODE (cs, bez prefixu).
    Якщо жодна альтернативна URL не резолвиться (сторінка поза i18n_patterns,
    напр. /admin/) — тег нічого не рендерить.
    """
    request = context.get('request')
    if request is None:
        return ''

    current_path = request.path
    entries = []
    seen_urls = set()

    for lang_code, _label in settings.LANGUAGES:
        translated_path = translate_url(current_path, lang_code)
        absolute_url = request.build_absolute_uri(translated_path)
        if absolute_url in seen_urls:
            continue
        seen_urls.add(absolute_url)
        entries.append((lang_code, absolute_url))

    # Якщо всі мови звелись до однієї й тієї ж URL — сторінка не мультимовна
    # (напр. поза i18n_patterns), hreflang тут не потрібен.
    if len(entries) <= 1:
        return ''

    default_path = translate_url(current_path, settings.LANGUAGE_CODE)
    default_url = request.build_absolute_uri(default_path)
    entries.append(('x-default', default_url))

    return format_html_join(
        '\n    ',
        '<link rel="alternate" hreflang="{}" href="{}">',
        entries,
    )
