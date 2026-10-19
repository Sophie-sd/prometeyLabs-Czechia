"""Квізи v2: латинські ключі у формах, legacy-кирилиця → ті ж ключі, людські назви в KeyCRM."""
import re
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.test import SimpleTestCase, TestCase, override_settings
from django.utils import translation

from apps.core.keycrm_service import KeyCRMService
from apps.core.models import FormSubmission
from apps.core.quiz_options import (
    QUIZ_FIELDS, format_quiz_answers, normalize_quiz_value,
)

ROOT = Path(__file__).resolve().parents[3]
CYR = re.compile(r'[А-Яа-яІіЇїЄєҐґ]')


class QuizNormalizeTests(SimpleTestCase):
    def test_keys_are_latin(self):
        for field, (_t, options) in QUIZ_FIELDS.items():
            for key in options:
                self.assertRegex(key, r'^[a-z0-9_]+$', field)

    def test_key_passthrough(self):
        self.assertEqual(normalize_quiz_value('q_timeline', 'flexible'), 'flexible')

    def test_legacy_cyrillic_maps_to_same_key(self):
        self.assertEqual(normalize_quiz_value('q_products', 'До 100 товарів'), 'up_to_100')
        self.assertEqual(normalize_quiz_value('q_timeline', 'Якнайшвидше (до 2 тижнів)'), 'asap_2w')
        self.assertEqual(normalize_quiz_value('q_pages', '1 сторінка (лендинг)'), 'landing')
        self.assertEqual(normalize_quiz_value('q_start', 'Міграція з Prom / OLX'), 'migration')

    def test_unknown_kept_truncated(self):
        self.assertEqual(normalize_quiz_value('q_goal', 'x' * 300), 'x' * 100)
        self.assertEqual(normalize_quiz_value('q_unknown', 'abc'), '')

    def test_format_readable(self):
        self.assertEqual(
            format_quiz_answers({'q_timeline': ['flexible'], 'q_features': ['seo_articles', 'crm_telegram']}),
            ['Додаткові опції: SEO + статті, CRM + Telegram', 'Терміни: Терміни гнучкі'],
        )


class QuizMarkupTests(SimpleTestCase):
    def _values(self, rel):
        text = (ROOT / rel).read_text(encoding='utf-8')
        return re.findall(r'name="(q_[a-z_]+)" value="([^"]*)"', text)

    def test_brief_values_are_known_latin_keys(self):
        for rel in ('templates/components/internet_shop_v2/brief.html',
                    'templates/components/corporate_website_v2/brief.html'):
            values = self._values(rel)
            self.assertTrue(values, rel)
            for field, value in values:
                self.assertFalse(CYR.search(value), (rel, value))
                self.assertIn(value, QUIZ_FIELDS[field][1], (rel, field, value))

    def test_js_scoring_uses_keys(self):
        for rel in ('static/js/internet-shop-v2-quiz.js', 'static/js/corporate-website-v2-quiz.js'):
            text = (ROOT / rel).read_text(encoding='utf-8')
            for literal in re.findall(r"=== '([^']*)'", text):
                self.assertFalse(CYR.search(literal), (rel, literal))


@mock.patch('apps.core.views._dispatch_async')
class QuizSubmissionTests(TestCase):
    def tearDown(self):
        translation.activate(settings.LANGUAGE_CODE)

    def _post(self, **quiz):
        data = {
            'form_type': 'site_request', 'name': 'TEST Jan', 'email': 'test@example.com',
            'consent': '1', 'details': 'TEST', 'source_page': '/internet-shop-v2/',
        }
        data.update(quiz)
        r = self.client.post('/forms/submit/', data)
        self.assertEqual(r.status_code, 200, r.content)
        return FormSubmission.objects.latest('id')

    def test_keys_saved(self, _d):
        sub = self._post(q_start='scratch', q_products='up_to_100',
                         q_features=['seo_articles', 'ads_promotion'], q_timeline='asap_2w')
        self.assertEqual(sub.extra_data['quiz_answers'], {
            'q_start': ['scratch'], 'q_products': ['up_to_100'],
            'q_features': ['seo_articles', 'ads_promotion'], 'q_timeline': ['asap_2w'],
        })

    def test_legacy_cyrillic_saved_as_keys(self, _d):
        sub = self._post(q_business='Торгівля', q_pages='до 10 сторінок', q_timeline='Терміни гнучкі')
        self.assertEqual(sub.extra_data['quiz_answers'], {
            'q_business': ['trade'], 'q_pages': ['up_to_10'], 'q_timeline': ['flexible'],
        })

    def test_no_quiz_no_key(self, _d):
        sub = self._post()
        self.assertNotIn('quiz_answers', sub.extra_data)

    @override_settings(KEYCRM_API_KEY='test-key-not-real')
    @mock.patch('apps.core.keycrm_service.requests.post')
    def test_keycrm_payload_readable(self, post, _d):
        resp = mock.Mock(status_code=201, text=''); resp.json.return_value = {'id': 1}
        post.return_value = resp
        sub = self._post(q_goal='online_sales', q_options='multilang', q_timeline='within_2w')
        KeyCRMService().create_pipeline_card(sub)
        comment = post.call_args.kwargs['json']['manager_comment']
        self.assertIn('=== КВІЗ ===', comment)
        self.assertIn('Бізнес-ціль: Прямі онлайн-продажі', comment)
        self.assertIn('Додаткові опції: Мультимовність', comment)
        self.assertIn('Терміни: Протягом 2 тижнів', comment)
        self.assertNotIn('online_sales', comment.split('=== КВІЗ ===')[1])
