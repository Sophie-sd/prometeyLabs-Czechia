from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include, re_path
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import TemplateView, RedirectView
from apps.core.i18n_views import set_language
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static

from apps.core.sitemaps import sitemaps

# URL без префіксу мови
urlpatterns = [
    path(
        'favicon.ico',
        RedirectView.as_view(url='/static/images/favicon.ico', permanent=True),
        name='favicon',
    ),
    path('admin/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')),
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
    # Media файли — завжди (Render Persistent Disk)
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

# URL з префіксом мови
urlpatterns += i18n_patterns(
    path('', include('apps.core.urls')),
    path('blog/', include('apps.blog.urls')),
    path('payment/', include('apps.payment.urls')),
    # Демо-магазини — тепер у i18n_patterns для презентації англомовним клієнтам
    path('demo/', include('apps.demoshop.urls', namespace='demoshop')),
    path('demo-landing/', include('apps.demolanding.urls', namespace='demolanding')),
    path('demo-site/', include('apps.democorp.urls', namespace='democorp')),
    prefix_default_language=False
)

# Статичні файли тільки для розробки
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
