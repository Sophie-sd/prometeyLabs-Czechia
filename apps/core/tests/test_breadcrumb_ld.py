from django.test import SimpleTestCase

from apps.core.ads_schema import breadcrumb_ld


class BreadcrumbLdTests(SimpleTestCase):
    def test_every_list_item_has_absolute_item(self):
        ld = breadcrumb_ld([
            {'name': 'Domů', 'url': 'https://prometeylabs.cz/'},
            {'name': 'Služby', 'url': ''},
            {'name': 'E-shop', 'url': 'https://prometeylabs.cz/internet-shop/'},
        ])
        elements = ld['itemListElement']
        self.assertEqual([e['position'] for e in elements], [1, 2])
        for e in elements:
            self.assertTrue(e['item'].startswith('https://'))
        self.assertEqual(elements[-1]['item'], 'https://prometeylabs.cz/internet-shop/')
