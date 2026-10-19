"""Data migration 0034: whatsapp_url заповнюється лише якщо порожнє; reverse чистить лише своє."""
import importlib
import re

from django.apps import apps as django_apps
from django.conf import settings
from django.core.cache import cache
from django.test import TestCase
from django.utils import translation

from apps.core.models import SiteContactSettings

MIG = importlib.import_module('apps.core.migrations.0034_sitecontactsettings_fill_whatsapp_url')
URL = MIG.WHATSAPP_URL
DIGITS = URL.rsplit('/', 1)[-1]


class WhatsAppDataMigrationTests(TestCase):
    def setUp(self):
        self.obj, _ = SiteContactSettings.objects.get_or_create(pk=1)

    def _set(self, value):
        SiteContactSettings.objects.filter(pk=1).update(whatsapp_url=value)

    def _value(self):
        return SiteContactSettings.objects.get(pk=1).whatsapp_url

    def test_url_is_wa_me(self):
        self.assertTrue(URL.startswith('https://wa.me/'))

    def test_migrated_test_db_has_url(self):
        # рядок pk=1 створює 0010, 0034 його заповнює
        self.assertEqual(self._value(), URL)

    def test_forward_fills_when_empty(self):
        self._set('')
        MIG.fill_whatsapp_url(django_apps, None)
        self.assertEqual(self._value(), URL)

    def test_forward_does_not_overwrite(self):
        self._set('https://wa.me/message/OTHER')
        MIG.fill_whatsapp_url(django_apps, None)
        self.assertEqual(self._value(), 'https://wa.me/message/OTHER')

    def test_forward_does_not_touch_phone(self):
        SiteContactSettings.objects.filter(pk=1).update(whatsapp_url='', phone_e164='', phone_display='')
        MIG.fill_whatsapp_url(django_apps, None)
        obj = SiteContactSettings.objects.get(pk=1)
        self.assertEqual((obj.phone_e164, obj.phone_display), ('', ''))

    def test_forward_without_row_creates_nothing(self):
        SiteContactSettings.objects.all().delete()  # лише тестова БД
        MIG.fill_whatsapp_url(django_apps, None)
        self.assertFalse(SiteContactSettings.objects.exists())

    def test_reverse_clears_own_value(self):
        self._set(URL)
        MIG.clear_own_whatsapp_url(django_apps, None)
        self.assertEqual(self._value(), '')

    def test_reverse_keeps_other_value(self):
        self._set('https://wa.me/message/OTHER')
        MIG.clear_own_whatsapp_url(django_apps, None)
        self.assertEqual(self._value(), 'https://wa.me/message/OTHER')

    def test_forward_is_idempotent(self):
        self._set('')
        MIG.fill_whatsapp_url(django_apps, None)
        MIG.fill_whatsapp_url(django_apps, None)
        self.assertEqual(self._value(), URL)


class WhatsAppButtonWithMigratedUrlTests(TestCase):
    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()
        translation.activate(settings.LANGUAGE_CODE)

    def test_button_rendered_from_migrated_url_and_number_hidden(self):
        for path in ('/', '/en/', '/contacts/', '/en/contacts/'):
            html = self.client.get(path).content.decode()
            if path in ('/', '/en/'):
                hero = re.search(r'<div class="hf-hero__actions">(.*?)</div>', html, re.S).group(1)
                link = re.search(r'<a [^>]*href="' + re.escape(URL) + r'"[^>]*>(.*?)</a>', hero, re.S)
                self.assertIsNotNone(link, path)
                self.assertEqual(link.group(1).strip(), 'WhatsApp')
            without_hrefs = re.sub(r'href="[^"]*"', 'href=""', html)
            self.assertNotIn(DIGITS, without_hrefs, path)
            self.assertNotIn(DIGITS[3:], without_hrefs, path)
            self.assertNotIn('+380', without_hrefs, path)
