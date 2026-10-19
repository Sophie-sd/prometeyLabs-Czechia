"""№70 (аудит 19.10.2026): категорія «courses» схована на .cz, але не видалена."""
from django.test import TestCase

from apps.blog.models import BlogPost


def make_post(slug, category):
    return BlogPost.objects.create(
        title=slug, slug=slug, excerpt='e', content='c', category=category,
        seo_title='s', seo_description='d', keywords='k', is_published=True,
    )


class HiddenBlogCategoryTests(TestCase):
    def setUp(self):
        self.visible = make_post('visible-post', 'web-development')
        self.hidden = make_post('courses-post', 'courses')

    def test_public_queryset_excludes_hidden_category(self):
        slugs = set(BlogPost.objects.public().values_list('slug', flat=True))
        self.assertEqual(slugs, {'visible-post'})
        # Нічого не видалено.
        self.assertTrue(BlogPost.objects.filter(slug='courses-post').exists())

    def test_list_and_detail(self):
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '/blog/courses-post/')
        self.assertNotContains(response, '?category=courses')
        self.assertEqual(self.client.get('/blog/courses-post/').status_code, 404)
        self.assertEqual(self.client.get('/blog/visible-post/').status_code, 200)

    def test_sitemap_excludes_hidden(self):
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'courses-post')
