from django.shortcuts import render
from django.core.paginator import Paginator
from django.views.generic import DetailView
from django.db.models import Q
from django.utils.translation import gettext as _
from django.utils import translation
from .models import BlogPost
from .seo import BLOG_LIST_META, blog_search_meta, post_meta, article_jsonld
from .visibility import is_hidden_category, visible_posts


def _lang():
    return (translation.get_language() or 'cs').split('-')[0]


def blog_list(request):
    """Список статей блогу з фільтрацією"""
    try:
        posts = visible_posts(BlogPost.objects.all())
        category = request.GET.get('category')
        if category:
            posts = posts.filter(category=category)
        
        # Пагінація
        paginator = Paginator(posts, 9)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Популярні статті
        popular_posts = visible_posts(BlogPost.objects.all()).order_by('-created_at')[:3]
        
    except Exception:
        # Fallback якщо таблиці не існують
        paginator = Paginator([], 9)
        page_obj = paginator.get_page(1)
        popular_posts = []
        category = None
    
    # №69, №70: мета /blog/ без «курсів програмування»; тексти CZ/EN у seo.py
    # (без нових gettext-рядків, .po не змінюється).
    meta = BLOG_LIST_META.get(_lang(), BLOG_LIST_META['cs'])
    context = {
        'page_obj': page_obj,
        'popular_posts': popular_posts,
        'category': category,
        'page_title': meta['title'],
        'meta_description': meta['description'],
        'og_title': meta['title'],
        'og_description': meta['description'],
        'keywords': meta['keywords'],
    }
    return render(request, 'pages/blog.html', context)


class BlogDetailView(DetailView):
    model = BlogPost
    template_name = 'pages/blog_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        try:
            return BlogPost.objects.filter(is_published=True)
        except Exception:
            return BlogPost.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        
        # SEO мета-дані. meta_title/meta_description/og_* у БД — чеські (seed),
        # тому для EN беремо H1 і лід статті (№72), див. seo.post_meta.
        context.update(post_meta(post, _lang()))
        context['keywords'] = post.get_localized_keywords()
        context['article_jsonld'] = article_jsonld(post, self.request.path, _lang())
        # Категорія «courses» на .cz прихована (№70): сторінка лишається, але noindex.
        context['seo_noindex'] = is_hidden_category(post.category)

        # Пов'язані статті
        related_posts = visible_posts(BlogPost.objects.filter(
            category=post.category,
        )).exclude(id=post.id)[:3]
        context['related_posts'] = related_posts
        
        return context


def blog_search(request):
    """Пошук по блогу"""
    query = request.GET.get('q', '')
    try:
        posts = visible_posts(BlogPost.objects.all())
        
        if query:
            posts = posts.filter(
                Q(title__icontains=query) |
                Q(title_en__icontains=query) |
                Q(title_cs__icontains=query) |
                Q(content__icontains=query) |
                Q(content_en__icontains=query) |
                Q(content_cs__icontains=query) |
                Q(keywords__icontains=query) |
                Q(keywords_en__icontains=query) |
                Q(keywords_cs__icontains=query)
            )
    except Exception:
        posts = BlogPost.objects.none()
    
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # №74: CZ/EN мета, keywords прибрано, сторінка noindex,follow (шаблон).
    meta = blog_search_meta(_lang(), query)
    context = {
        'page_obj': page_obj,
        'query': query,
        'page_title': meta['title'],
        'meta_description': meta['description'],
        'og_title': meta['title'],
        'og_description': meta['description'],
        'keywords': '',
    }
    
    return render(request, 'pages/blog_search.html', context)
