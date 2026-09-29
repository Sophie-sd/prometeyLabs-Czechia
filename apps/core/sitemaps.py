"""Sitemap для Google Search Console / краулерів."""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.blog.models import BlogPost

SITE_DOMAIN = 'www.prometeylabs.com'


class AbsoluteSitemap(Sitemap):
    """Sitemap без django.contrib.sites — фіксований прод-домен."""

    protocol = 'https'

    def get_urls(self, page=1, site=None, protocol=None):
        class _Site:
            domain = SITE_DOMAIN
            name = 'PrometeyLabs'

        return super().get_urls(
            page=page,
            site=_Site(),
            protocol=protocol or self.protocol,
        )


class StaticViewSitemap(AbsoluteSitemap):
    """Публічні маркетингові та юридичні сторінки."""

    changefreq = 'weekly'
    priority = 0.7

    # hreflang alternates у sitemap.xml (дублює <link rel="alternate"> —
    # рекомендація Google для мультимовних сайтів).
    i18n = True
    alternates = True
    x_default = True

    # name → (priority, changefreq)
    PAGES = {
        'home': (1.0, 'daily'),
        'portfolio': (0.9, 'weekly'),
        'internet_shop_v2': (0.9, 'weekly'),
        'corporate_website_v2': (0.9, 'weekly'),
        'telegram_bot': (0.9, 'weekly'),
        'tz_generator': (0.9, 'weekly'),
        'calculator': (0.8, 'weekly'),
        'contacts': (0.8, 'monthly'),
        'developer': (0.6, 'monthly'),
        'monobank_chastynamy': (0.5, 'monthly'),
        'offer': (0.3, 'yearly'),
        'privacy': (0.3, 'yearly'),
        'cookies': (0.3, 'yearly'),
        'refund': (0.3, 'yearly'),
        'intellectual_property': (0.3, 'yearly'),
        'blog:blog_list': (0.8, 'daily'),
    }

    def items(self):
        return list(self.PAGES.keys())

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return self.PAGES[item][0]

    def changefreq(self, item):
        return self.PAGES[item][1]


class BlogPostSitemap(AbsoluteSitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return BlogPost.objects.filter(is_published=True).only('slug', 'updated_at')

    def lastmod(self, obj):
        return obj.updated_at


sitemaps = {
    'static': StaticViewSitemap,
    'blog': BlogPostSitemap,
}
