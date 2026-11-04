import re

from django.http import HttpResponsePermanentRedirect
from django.urls import path, re_path, reverse

from . import views
from .slug_map import OLD_TO_NEW

app_name = 'blog'


def legacy_slug_redirect(request, old):
    """One-hop 301 old slug → Czech slug (with or without trailing slash; query string kept)."""
    target = reverse('blog:blog_detail', kwargs={'slug': OLD_TO_NEW[old]})
    query = request.META.get('QUERY_STRING', '')
    return HttpResponsePermanentRedirect(f'{target}?{query}' if query else target)


_OLD_RE = '|'.join(re.escape(s) for s in sorted(OLD_TO_NEW, key=len, reverse=True))

urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    path('search/', views.blog_search, name='blog_search'),
    re_path(rf'^(?P<old>{_OLD_RE})/?$', legacy_slug_redirect, name='blog_legacy_redirect'),
    re_path(r'^(?P<slug>[-\w\u0400-\u04FF.]+)/$', views.BlogDetailView.as_view(), name='blog_detail'),
]
