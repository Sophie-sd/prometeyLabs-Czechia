"""
URL configuration for prometey_project project.

Mirrors `config/urls.py` (used in production) so local dev exposes the same
language-prefixed URLs (e.g. `/ru/internet-shop/`) as production. Without
i18n_patterns here, RU prefixed URLs would 404 locally.
"""
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include, re_path
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import TemplateView
from apps.core.i18n_views import set_language
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static

from apps.core.sitemaps import sitemaps

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/set_language/', set_language, name='set_language'),
    path(
        'robots.txt',
        TemplateView.as_view(template_name='robots.txt', content_type='text/plain'),
        name='robots_txt',
    ),
    path(
        'sitemap.xml',
        sitemap,
        {'sitemaps': sitemaps},
        name='sitemap',
    ),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

urlpatterns += i18n_patterns(
    path('', include('apps.core.urls')),
    path('blog/', include('apps.blog.urls')),
    path('payment/', include('apps.payment.urls')),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
