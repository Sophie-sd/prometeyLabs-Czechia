"""Які статті блогу показуються на prometeylabs.cz.

Категорія «Kurzy programování / Programming Courses» (courses) — український
бізнес курсів, на .cz її ховаємо (завдання №70). Дані в БД не змінюються і
не видаляються: статті лише відфільтровуються зі списків, пошуку, «related»,
sitemap, а сама сторінка статті отримує noindex.
"""

HIDDEN_BLOG_CATEGORIES = frozenset({'courses'})


def is_hidden_category(category) -> bool:
    return (category or '') in HIDDEN_BLOG_CATEGORIES


def visible_posts(queryset):
    """Опубліковані статті без прихованих на .cz категорій."""
    return queryset.filter(is_published=True).exclude(category__in=HIDDEN_BLOG_CATEGORIES)
