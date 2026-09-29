"""Custom set_language with prefix_default_language=False (cs default, en prefixed)."""
from django.conf import settings
from django.test import SimpleTestCase, override_settings
from django.urls import reverse

from apps.core.i18n_views import strip_lang_prefix, translate_path


@override_settings(
    LANGUAGE_CODE='cs',
    LANGUAGES=[('cs', 'Čeština'), ('en', 'English')],
)
class TranslatePathTests(SimpleTestCase):
    def test_strip_en_prefix(self):
        self.assertEqual(strip_lang_prefix('/en/'), '/')
        self.assertEqual(strip_lang_prefix('/en'), '/')
        self.assertEqual(strip_lang_prefix('/en/demo/x/'), '/demo/x/')

    def test_strip_leaves_default_path(self):
        self.assertEqual(strip_lang_prefix('/demo/x/'), '/demo/x/')
        self.assertEqual(strip_lang_prefix('/contacts/'), '/contacts/')

    def test_cs_from_en_root(self):
        self.assertEqual(translate_path('/en/', 'cs'), '/')

    def test_en_demo_from_unprefixed(self):
        self.assertEqual(translate_path('/demo/x/', 'en'), '/en/demo/x/')

    def test_cs_demo_from_en(self):
        self.assertEqual(translate_path('/en/demo/x/', 'cs'), '/demo/x/')

    def test_en_contacts(self):
        self.assertEqual(translate_path('/contacts/', 'en'), '/en/contacts/')

    def test_keeps_query_string(self):
        self.assertEqual(
            translate_path('/en/demo/x/?q=1', 'cs'),
            '/demo/x/?q=1',
        )


@override_settings(
    ROOT_URLCONF='config.urls',
    LANGUAGE_CODE='cs',
    LANGUAGES=[('cs', 'Čeština'), ('en', 'English')],
)
class SetLanguageViewTests(SimpleTestCase):
    def test_cs_from_en_root_location(self):
        response = self.client.post(
            reverse('set_language'),
            {'language': 'cs', 'next': '/en/'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/')
        self.assertEqual(
            response.cookies[settings.LANGUAGE_COOKIE_NAME].value,
            'cs',
        )

    def test_en_demo_location(self):
        response = self.client.post(
            reverse('set_language'),
            {'language': 'en', 'next': '/demo/x/'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/en/demo/x/')

    def test_cs_from_en_demo_location(self):
        response = self.client.post(
            reverse('set_language'),
            {'language': 'cs', 'next': '/en/demo/x/'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/demo/x/')

    def test_en_contacts_location(self):
        response = self.client.post(
            reverse('set_language'),
            {'language': 'en', 'next': '/contacts/'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/en/contacts/')

    def test_rejects_offsite_next(self):
        response = self.client.post(
            reverse('set_language'),
            {'language': 'cs', 'next': 'https://evil.example/'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/')
