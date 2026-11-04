from django.test import TestCase, override_settings

from apps.blog.models import BlogPost
from apps.blog.slug_map import OLD_TO_NEW


@override_settings(SECURE_SSL_REDIRECT=False)
class CzechSlugRedirectTests(TestCase):
    def setUp(self):
        for i, new in enumerate(OLD_TO_NEW.values()):
            BlogPost.objects.create(title=f'P{i}', slug=new, content='x', is_published=True)

    def test_old_slugs_single_301_to_final_200(self):
        for old, new in OLD_TO_NEW.items():
            for pre in ('', '/en'):
                for tail in ('/', ''):
                    with self.subTest(old=old, pre=pre, tail=tail):
                        r = self.client.get(f'{pre}/blog/{old}{tail}')
                        self.assertEqual(r.status_code, 301)
                        self.assertEqual(r['Location'], f'{pre}/blog/{new}/')
                        self.assertEqual(self.client.get(r['Location']).status_code, 200)

    def test_sitemap_has_no_old_slugs(self):
        xml = self.client.get('/sitemap.xml').content.decode()
        for old in OLD_TO_NEW:
            self.assertNotIn(old, xml)
