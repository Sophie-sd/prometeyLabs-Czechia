"""SEO-мета блогу для prometeylabs.cz (cs/en).

Тексти тут — літерали по мові, а не gettext, щоб не додавати msgid у .po
(.po веде Copy). Тільки cs/en; інші мови падають на cs.
"""
import json

from django.utils.html import strip_tags

from apps.core.templatetags.seo_tags import absolute

# №69 (keywords) + №70 (title без «курсів програмування»).
BLOG_LIST_META = {
    'cs': {
        'title': 'Blog o tvorbě webů, e-shopech a automatizaci',
        'description': (
            'Praktické články o tvorbě webů, e-shopech, Telegram botech, AI a SEO '
            'od týmu PrometeyLabs.'
        ),
        'keywords': 'tvorba webů, e-shopy, Telegram boti, AI, SEO',
    },
    'en': {
        'title': 'Blog on web development, e-commerce and automation',
        'description': (
            'Practical articles on web development, e-commerce, Telegram bots, AI and SEO '
            'from the PrometeyLabs team.'
        ),
        'keywords': 'web development, e-commerce, Telegram bots, AI, SEO',
    },
}


def blog_search_meta(lang: str, query: str) -> dict:
    """№74: /blog/search/ і /en/blog/search/."""
    query = (query or '').strip()
    if lang == 'en':
        return {
            'title': 'Blog search | PrometeyLabs',
            'description': (
                f'Search results for “{query}” in the blog'
                if query else 'Search the PrometeyLabs blog'
            ),
        }
    return {
        'title': 'Hledání v blogu | PrometeyLabs',
        'description': (
            f'Výsledky hledání „{query}“ v blogu'
            if query else 'Hledání v blogu PrometeyLabs'
        ),
    }


def _clip(text: str, limit: int) -> str:
    """Обрізати по межі слова, без «…» посеред слова."""
    text = ' '.join(strip_tags(text or '').split())
    if len(text) <= limit:
        return text
    cut = text[:limit + 1].rsplit(' ', 1)[0].rstrip(' ,;:–—-')
    return cut + '…'


def post_meta(post, lang: str) -> dict:
    """Title / description / og:* статті для активної мови.

    CS — як і раніше, з полів meta_title / meta_description / og_* (чеські).
    EN (№72) — з H1 (title_en) і ліду (excerpt_en), бо meta_* у БД чеські.
    """
    if lang == 'en' and (post.title_en or '').strip():
        title = ' '.join(strip_tags(post.title_en).split())
        description = _clip(post.excerpt_en or '', 160)
        return {
            'page_title': title,
            'meta_description': description,
            'og_title': title,
            'og_description': description,
        }
    return {
        'page_title': post.meta_title or strip_tags(post.get_localized_title()),
        'meta_description': post.meta_description or _clip(post.get_localized_excerpt(), 160),
        'og_title': post.og_title or strip_tags(post.get_localized_title()),
        'og_description': post.og_description or _clip(post.get_localized_excerpt(), 160),
    }


def article_jsonld(post, path: str, lang: str) -> str:
    """Article JSON-LD лише з реальних полів статті (без рейтингів/метрик)."""
    meta = post_meta(post, lang)
    url = absolute(path)
    data = {
        '@context': 'https://schema.org',
        '@type': 'Article',
        'headline': meta['page_title'][:110],
        'description': meta['meta_description'],
        'inLanguage': lang if lang in ('cs', 'en') else 'cs',
        'mainEntityOfPage': {'@type': 'WebPage', '@id': url},
        'url': url,
        'author': {'@type': 'Organization', 'name': 'PrometeyLabs', 'url': absolute('/')},
        'publisher': {'@type': 'Organization', 'name': 'PrometeyLabs', 'url': absolute('/')},
    }
    if post.created_at:
        data['datePublished'] = post.created_at.isoformat()
    # dateModified свідомо не ставимо: updated_at оновлює щоденний seed, а не
    # редакція статті — це була б неправдива «свіжість».
    if post.featured_image:
        try:
            data['image'] = absolute(post.featured_image.url)
        except ValueError:
            pass
    raw = json.dumps(data, ensure_ascii=False, indent=2)
    # Безпечно всередині <script>: не дати закрити тег.
    return raw.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
