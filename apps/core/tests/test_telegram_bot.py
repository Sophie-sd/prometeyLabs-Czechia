"""Telegram-bot money page: routes, sitemap, i18n, form."""
import json

from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from apps.core.i18n_views import translate_path
from apps.core.models import FormSubmission
from apps.core.sitemaps import StaticViewSitemap


class TelegramBotPageTests(TestCase):
    def test_reverse_default_path(self):
        self.assertEqual(reverse('telegram_bot'), '/telegram-bot/')

    def test_get_cs_en_200(self):
        for lang, path in (
            ('cs', '/telegram-bot/'),
            ('en', '/en/telegram-bot/'),
        ):
            with self.subTest(lang=lang):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                html = response.content.decode()
                self.assertIn('plBotRoot', html)
                self.assertIn('telegram-bot.css', html)
                self.assertIn('pl-product-tokens.css', html)
                self.assertNotIn('internet-shop-v2.js', html)
                self.assertNotIn('internet-shop-v2.css', html)
                self.assertNotIn('internet-shop-v2-anim.css', html)
                self.assertNotIn('corporate-website-v2-anim.css', html)
                self.assertNotIn('tz-generator-', html)
                self.assertNotIn('shop_hero', html)
                self.assertNotIn('id="tzRoot"', html)
                self.assertIn('application/ld+json', html)
                self.assertIn('FAQPage', html)
                self.assertIn('name="source_page"', html)
                self.assertIn('value="telegram-bot"', html)
                self.assertIn('data-form-type="telegram-bot"', html)
                self.assertIn('data-qa="lead-form"', html)
                self.assertNotIn('data-testid="lead-form"', html)
                self.assertIn('name="honeypot"', html)
                self.assertIn('class="pl-bot__honeypot"', html)
                self.assertIn('id="pl-bot-form"', html)
                self.assertIn('pl-bot__demo', html)
                self.assertIn('pl-bot__tg-thread', html)

    def test_section_order_and_cta_copy(self):
        html = self.client.get('/telegram-bot/').content.decode()
        who = html.find('id="pl-bot-who-title"')
        process = html.find('id="pl-bot-process-title"')
        pkg = html.find('id="pl-bot-pkg-title"')
        price = html.find('id="pl-bot-price-title"')
        faq = html.find('id="pl-bot-faq"')
        form = html.find('id="pl-bot-form"')
        self.assertTrue(0 < who < process < pkg < price < faq < form)
        self.assertNotIn('id="pl-bot-int-title"', html)
        self.assertNotIn('Надіслати бриф', html)
        self.assertNotRegex(
            html,
            r'<button\b[^>]*type="submit"[^>]*>\s*Отримати кошторис\s*</button>',
        )
        self.assertRegex(
            html,
            r'<a\b[^>]*href="#pl-bot-form"[^>]*>\s*Отримати прорахунок\s*</a>',
        )
        self.assertRegex(
            html,
            r'<button\b[^>]*type="submit"[^>]*>\s*Отримати прорахунок\s*</button>',
        )
        self.assertIn('id="pl-bot-form-title"', html)
        self.assertGreaterEqual(html.count('Отримати прорахунок'), 2)

    def test_hreflang_and_canonical_use_url_tag_pattern(self):
        html = self.client.get('/telegram-bot/').content.decode()
        self.assertIn('https://www.prometeylabs.com/telegram-bot/', html)
        self.assertIn('hreflang="cs"', html)
        self.assertIn('hreflang="en"', html)
        self.assertIn('hreflang="x-default"', html)
        self.assertNotIn('PageSpeed', html)
        self.assertNotIn('LCP 0.8', html)
        self.assertNotIn('0.8s', html)
        self.assertNotIn('lighthouse', html.lower())

    def test_existing_money_routes_still_200(self):
        for name in (
            'home',
            'internet_shop_v2',
            'corporate_website_v2',
            'calculator',
            'tz_generator',
            'portfolio',
            'blog:blog_list',
            'contacts',
        ):
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertIn(response.status_code, (200, 302))

    def test_footer_points_to_telegram_bot(self):
        html = self.client.get('/').content.decode()
        self.assertIn('href="/telegram-bot/"', html)


class TelegramBotSitemapTests(SimpleTestCase):
    def test_pages_include_telegram_and_shop(self):
        pages = StaticViewSitemap.PAGES
        self.assertIn('telegram_bot', pages)
        self.assertIn('internet_shop_v2', pages)
        self.assertEqual(pages['telegram_bot'][0], 0.9)

    def test_reverse_all_static_sitemap_names(self):
        for name in StaticViewSitemap.PAGES:
            with self.subTest(name=name):
                self.assertTrue(reverse(name))


class TelegramBotSitemapResponseTests(TestCase):
    def test_sitemap_xml_contains_bot_and_shop(self):
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        text = response.content.decode()
        self.assertIn('/telegram-bot/', text)
        self.assertIn('/internet-shop-v2/', text)


class TelegramBotFormTests(TestCase):
    def setUp(self):
        self.submit_url = reverse('form_submit')

    def test_telegram_bot_form_saves_distinct_type(self):
        response = self.client.post(self.submit_url, {
            'form_type': 'telegram-bot',
            'name': 'Олена Бот',
            'phone': '+380631234567',
            'source_page': 'telegram-bot',
            'bot_task': 'Заявки та кваліфікація ліда',
            'details': 'Потрібен бот для запису',
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        submission = FormSubmission.objects.latest('id')
        self.assertEqual(submission.form_type, 'telegram-bot')
        self.assertIn('/telegram-bot/', submission.details)
        extra = submission.extra_data or {}
        self.assertEqual(extra.get('source_page'), 'telegram-bot')

    def test_telegram_bot_underscore_alias(self):
        response = self.client.post(self.submit_url, {
            'form_type': 'telegram_bot',
            'name': 'Олена Бот',
            'phone': '+380631234567',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json.loads(response.content)['success'])
        self.assertEqual(FormSubmission.objects.latest('id').form_type, 'telegram-bot')

    def test_filled_honeypot_is_silent_success_without_save(self):
        before = FormSubmission.objects.count()
        response = self.client.post(self.submit_url, {
            'form_type': 'telegram-bot',
            'name': 'Олена Бот',
            'phone': '+380631234567',
            'source_page': 'telegram-bot',
            'honeypot': 'bot-filled',
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(FormSubmission.objects.count(), before)

    def test_unknown_form_type_does_not_500(self):
        response = self.client.post(self.submit_url, {
            'form_type': 'not-a-real-type',
            'name': 'Олена Бот',
            'phone': '+380631234567',
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data['success'])


@override_settings(ROOT_URLCONF='config.urls')
class TelegramBotI18nPathTests(SimpleTestCase):
    def test_translate_path_cs_to_en(self):
        self.assertEqual(translate_path('/telegram-bot/', 'en'), '/en/telegram-bot/')

    def test_translate_path_en_to_cs(self):
        self.assertEqual(translate_path('/en/telegram-bot/', 'cs'), '/telegram-bot/')

    def test_set_language_from_bot_page(self):
        response = self.client.post(
            reverse('set_language'),
            {'language': 'en', 'next': '/telegram-bot/'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/en/telegram-bot/')
