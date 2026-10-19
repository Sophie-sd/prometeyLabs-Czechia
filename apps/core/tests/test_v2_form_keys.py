"""#12: службові поля форм v2 латиницею; людські назви для менеджера — на сервері."""
import re
from html.parser import HTMLParser
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.test import SimpleTestCase, TestCase, override_settings
from django.utils import translation

from apps.core.keycrm_service import KeyCRMService
from apps.core.models import FormSubmission
from apps.core.quiz_options import humanize_details, resolve_lead_name, source_label

ROOT = Path(__file__).resolve().parents[3]
CYR = re.compile('[\u0400-\u04FF]')
V2_PAGES = ('/corporate-website/', '/en/corporate-website/', '/internet-shop/', '/en/internet-shop/')


class _FormValueScanner(HTMLParser):
    """Збирає те, що форма відправляє на сервер: value/name полів (крім введених
    користувачем text/tel/email) та data-source-label форм."""
    USER_TYPES = {'text', 'tel', 'email', 'password', 'search', 'url'}

    def __init__(self):
        super().__init__()
        self.depth = 0
        self.values = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'form':
            self.depth += 1
            if a.get('data-source-label'):
                self.values.append(('data-source-label', a['data-source-label']))
        if not self.depth or tag not in ('input', 'option', 'button', 'select', 'textarea'):
            return
        if tag == 'input' and a.get('type') in self.USER_TYPES:
            return
        for key in ('name', 'value'):
            if a.get(key):
                self.values.append((f'{tag}[{a.get("name")}].{key}', a[key]))

    def handle_endtag(self, tag):
        if tag == 'form' and self.depth:
            self.depth -= 1


class RenderedV2FormsTests(TestCase):
    def tearDown(self):
        translation.activate(settings.LANGUAGE_CODE)

    def test_no_cyrillic_in_submitted_form_values(self):
        for url in V2_PAGES:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, url)
            scanner = _FormValueScanner()
            scanner.feed(response.content.decode())
            self.assertTrue(scanner.values, url)
            bad = [(k, v) for k, v in scanner.values if CYR.search(v)]
            self.assertEqual(bad, [], url)

    def test_keys_present_in_markup(self):
        corp = self.client.get('/corporate-website/').content.decode()
        self.assertIn('name="name" value="free_analysis"', corp)
        self.assertIn('data-source-label="corporate_website_v2"', corp)
        shop = self.client.get('/en/internet-shop/').content.decode()
        self.assertIn('data-source-label="internet_shop_v2"', shop)
        self.assertIn('data-source-label="internet_shop_v2_hero"', shop)
        self.assertIn('name="details" value="page: internet_shop_v2_hero"', shop)


class QuizJsStringsTests(SimpleTestCase):
    # uk-блок PKG_MAP (fallback, не використовується на cs/en) прибирає cz/frontend.
    UK_BLOCK = re.compile(r'\n        uk: \{.*?\n        \},\n', re.S)

    def test_no_cyrillic_strings_sent_to_server(self):
        for rel in ('static/js/corporate-website-v2-quiz.js', 'static/js/internet-shop-v2-quiz.js'):
            text = self.UK_BLOCK.sub('\n', (ROOT / rel).read_text(encoding='utf-8'))
            bad = [line.strip() for line in text.splitlines() if CYR.search(line)]
            self.assertEqual(bad, [], rel)


class ServerMappingTests(SimpleTestCase):
    def test_source_label(self):
        self.assertEqual(source_label('internet_shop_v2_hero'), 'Інтернет-магазин v2 · Форма на першому екрані')
        self.assertEqual(source_label('Інтернет-магазин v2 · перший екран'), 'Інтернет-магазин v2 · Форма на першому екрані')
        self.assertEqual(source_label('unknown'), 'unknown')

    def test_lead_name(self):
        self.assertEqual(resolve_lead_name('free_analysis'), 'Bezplatná analýza')
        self.assertEqual(resolve_lead_name('Безкоштовний аналіз'), 'Bezplatná analýza')
        self.assertEqual(resolve_lead_name('Jan Novák'), 'Jan Novák')

    def test_humanize_details_keys(self):
        raw = ('page: corporate_website_v2\npackage: START · 5–7 dní\n'
               'q_goal: online_sales\nq_options: ads, multilang\nq_timeline: within_2w')
        self.assertEqual(humanize_details(raw), (
            'Сторінка: Корпоративний сайт v2\nРекомендований пакет: START · 5–7 dní\n'
            'Бізнес-ціль: Прямі онлайн-продажі\nДодаткові опції: Рекламні послуги, Мультимовність\n'
            'Терміни: Протягом 2 тижнів'))

    def test_humanize_details_shop_and_hint(self):
        raw = 'page: internet_shop_v2\nq_features: crm_telegram\npkg_hint: PREMIUM'
        self.assertEqual(humanize_details(raw), (
            'Сторінка: Інтернет-магазин v2\nДодаткові опції: CRM + Telegram\n'
            'Підказка з картки пакета: PREMIUM'))

    def test_humanize_details_legacy_unchanged(self):
        legacy = 'Сторінка: Інтернет-магазин v2\nТерміни: Терміни гнучкі\nвільний текст'
        self.assertEqual(humanize_details(legacy), legacy)

    def test_humanize_details_mixed_legacy_values(self):
        self.assertEqual(humanize_details('page: Корпоративний сайт v2\nq_pages: до 10 сторінок'),
                         'Сторінка: Корпоративний сайт v2\nКількість сторінок: до 10 сторінок')


@mock.patch('apps.core.views._dispatch_async')
class SubmissionMappingTests(TestCase):
    def tearDown(self):
        translation.activate(settings.LANGUAGE_CODE)

    def _keycrm_payload(self, submission):
        with override_settings(KEYCRM_API_KEY='test-key-not-real'), \
                mock.patch('apps.core.keycrm_service.requests.post') as post:
            resp = mock.Mock(status_code=201, text='')
            resp.json.return_value = {'id': 1}
            post.return_value = resp
            KeyCRMService().create_pipeline_card(submission)
        return post.call_args.kwargs['json']

    def _free_analysis(self, name):
        r = self.client.post('/forms/submit/', {
            'form_type': 'call_request', 'source_page': 'corporate-website-v2-free-analysis',
            'name': name, 'phone': '+420 777 123 456', 'consent': '1',
        })
        self.assertEqual(r.status_code, 200, r.content)
        return FormSubmission.objects.latest('id')

    def test_free_analysis_card_title_readable(self, _d):
        sub = self._free_analysis('free_analysis')
        self.assertEqual(sub.name, 'Bezplatná analýza')
        payload = self._keycrm_payload(sub)
        self.assertTrue(payload['title'].endswith(' - Bezplatná analýza'), payload['title'])
        self.assertFalse(CYR.search(payload['title']), payload['title'])

    def test_free_analysis_legacy_cyrillic_name(self, _d):
        sub = self._free_analysis('Безкоштовний аналіз')
        self.assertEqual(sub.name, 'Bezplatná analýza')
        self.assertFalse(CYR.search(self._keycrm_payload(sub)['title']))

    def test_site_request_details_humanized(self, _d):
        r = self.client.post('/forms/submit/', {
            'form_type': 'site_request', 'name': 'TEST Jan', 'email': 'test@example.com',
            'consent': '1', 'source_page': 'internet-shop-v2',
            'details': 'page: internet_shop_v2_hero',
        })
        self.assertEqual(r.status_code, 200, r.content)
        sub = FormSubmission.objects.latest('id')
        payload = self._keycrm_payload(sub)
        self.assertIn('Сторінка: Інтернет-магазин v2 · Форма на першому екрані', payload['manager_comment'])
        self.assertNotIn('internet_shop_v2_hero', payload['manager_comment'])
