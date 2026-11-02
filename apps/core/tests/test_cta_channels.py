"""Canon: the one primary hero CTA is the quiz; WhatsApp only when filled in the CMS."""
import re

from django.conf import settings
from django.core.cache import cache
from django.utils import translation
from django.test import TestCase

from apps.core.models import SiteContactSettings


class HomeCtaChannelsTests(TestCase):
    def setUp(self):
        cache.clear()
        self.contacts, _ = SiteContactSettings.objects.get_or_create(pk=1)
        self.contacts.phone_e164 = ''
        self.contacts.whatsapp_url = ''
        self.contacts.save()

    def tearDown(self):
        cache.clear()
        # GET /en/ лишає активну мову en у потоці тестів → reverse() в інших тестах дасть /en/…
        translation.activate(settings.LANGUAGE_CODE)

    def _hero(self, html):
        start = html.index('<div class="hf-hero__actions')
        return html[start:html.index('</section>', start)]

    def test_primary_hero_cta_is_the_quiz(self):
        """One primary action on the first screen; Telegram and the modal are ghost buttons."""
        hero = self._hero(self.client.get('/').content.decode())
        primary = re.search(r'<a[^>]*class="pl-calc-cta__btn[^"]*"[^>]*>', hero)
        self.assertIsNotNone(primary)
        self.assertIn('data-calc-cta="hero"', primary.group(0))
        self.assertNotIn('hf-btn--light', hero)
        modal = re.search(r'<button[^>]*data-modal="call-request-modal"[^>]*>', hero).group(0)
        self.assertIn('hf-btn--ghost', modal)

    def test_whatsapp_hidden_when_empty(self):
        html = self.client.get('/').content.decode()
        self.assertNotIn('wa.me', html)

    def test_whatsapp_shown_when_filled_in_cms(self):
        """The hero keeps three buttons; WhatsApp lives in the bottom CTA section."""
        self.contacts.whatsapp_url = 'https://wa.me/message/TESTONLY'
        self.contacts.save()
        cache.clear()
        html = self.client.get('/').content.decode()
        self.assertNotIn('wa.me', self._hero(html))
        cta = re.search(r'<div class="hf-cta__actions">(.*?)</div>\s*</div>', html, re.S).group(1)
        self.assertIn('https://wa.me/message/TESTONLY', cta)

    def test_cta_section_primary_is_form(self):
        html = self.client.get('/').content.decode()
        cta = re.search(r'<div class="hf-cta__actions">(.*?)</div>', html, re.S).group(1)
        first = re.search(r'<(?:a|button)[^>]*>', cta).group(0)
        self.assertIn('data-modal="call-request-modal"', first)
        self.assertIn('hf-btn--light', first)

    def test_cs_telegram_casing(self):
        html = self.client.get('/').content.decode()
        self.assertNotIn('Napsat na telegram', html)
        self.assertNotIn('telegram konzultace', html)
        self.assertIn('Napsat na Telegram', html)
        self.assertIn('Konzultace přes Telegram', html)


class HomeWhatsAppOnlyFromUrlTests(TestCase):
    """WhatsApp у CTA головної — лише з whatsapp_url; номер тільки всередині href."""

    FAKE_DIGITS = '111222333444'  # тестові цифри, не реальний номер

    def setUp(self):
        cache.clear()
        self.contacts, _ = SiteContactSettings.objects.get_or_create(pk=1)

    def tearDown(self):
        cache.clear()
        # GET /en/ лишає активну мову en у потоці тестів → reverse() в інших тестах дасть /en/…
        translation.activate(settings.LANGUAGE_CODE)

    def _save(self, **fields):
        for k, v in fields.items():
            setattr(self.contacts, k, v)
        self.contacts.save()
        cache.clear()

    def _sections(self, html):
        start = html.index('<div class="hf-hero__actions')
        hero = html[start:html.index('</section>', start)]
        cta = re.search(r'<div class="hf-cta__actions">(.*?)</div>\s*</div>', html, re.S).group(1)
        return hero, cta

    def test_absent_when_url_empty_even_if_phone_set(self):
        self._save(whatsapp_url='', phone_e164=self.FAKE_DIGITS, phone_display='')
        hero, cta = self._sections(self.client.get('/').content.decode())
        for block in (hero, cta):
            self.assertNotIn('WhatsApp', block)
            self.assertNotIn('wa.me', block)

    def test_present_with_wa_me_href_when_url_set(self):
        """Canon hero has no WhatsApp button; the bottom CTA section still offers it."""
        url = f'https://wa.me/{self.FAKE_DIGITS}'
        self._save(whatsapp_url=url, phone_e164='', phone_display='')
        for path in ('/', '/en/'):
            hero, cta = self._sections(self.client.get(path).content.decode())
            self.assertNotIn('wa.me', hero, path)
            link = re.search(r'<a [^>]*href="https://wa\.me/[^"]*"[^>]*>(.*?)</a>', cta, re.S)
            self.assertIsNotNone(link, path)
            self.assertIn(f'href="{url}"', link.group(0))
            self.assertEqual(link.group(1).strip(), 'WhatsApp')

    def test_number_never_visible_outside_href(self):
        self._save(whatsapp_url=f'https://wa.me/{self.FAKE_DIGITS}', phone_e164='', phone_display='')
        for path in ('/', '/en/'):
            html = self.client.get(path).content.decode()
            without_hrefs = re.sub(r'href="[^"]*"', 'href=""', html)
            self.assertNotIn(self.FAKE_DIGITS, without_hrefs, path)
            self.assertNotIn('+380', without_hrefs, path)
            for attr in re.findall(r'(?:aria-label|title)="([^"]*)"', html):
                self.assertNotIn(self.FAKE_DIGITS, attr)
