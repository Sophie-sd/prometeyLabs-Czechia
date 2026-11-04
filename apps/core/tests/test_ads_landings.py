"""Google Ads landing pages must answer 200 (never 301 to home), self-canonical, in sitemap."""
from django.test import TestCase, override_settings

ADS_LANDINGS = {
    # path: canonical path (self)
    '/web-development/': '/web-development/',
    '/en/web-development/': '/en/web-development/',
    '/webove-aplikace/': '/webove-aplikace/',
    '/en/web-applications/': '/en/web-applications/',
}


@override_settings(SECURE_SSL_REDIRECT=False)
class AdsLandingPagesTests(TestCase):
    def test_landings_200_self_canonical(self):
        for path, canon in ADS_LANDINGS.items():
            for suffix in ('', '?gclid=test'):
                with self.subTest(path=path + suffix):
                    r = self.client.get(path + suffix)
                    self.assertEqual(r.status_code, 200)
                    html = r.content.decode()
                    self.assertIn(f'<link rel="canonical" href="https://prometeylabs.cz{canon}">', html)
                    self.assertIn('hreflang="x-default"', html)

    def test_landings_in_sitemap(self):
        xml = self.client.get('/sitemap.xml').content.decode()
        for canon in ADS_LANDINGS.values():
            with self.subTest(canon=canon):
                self.assertIn(f'<loc>https://prometeylabs.cz{canon}</loc>', xml)
