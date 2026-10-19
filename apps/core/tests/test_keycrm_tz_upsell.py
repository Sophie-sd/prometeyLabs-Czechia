"""
TZ upsell не створює другу картку KeyCRM (оновлює існуючу).
requests.post / requests.put замокано — жодних живих запитів у KeyCRM.
"""
import json
from datetime import timedelta
from unittest import mock

from django.test import TestCase, override_settings
from django.utils import timezone

from apps.core.keycrm_service import sync_submission_to_keycrm, sync_tz_upsell_to_keycrm
from apps.core.models import FormSubmission

TOKEN = 'test-token-upsell'


def _resp(status=201, card_id=555):
    r = mock.Mock(status_code=status, text='')
    r.json.return_value = {'id': card_id}
    return r


@override_settings(KEYCRM_API_KEY='test-key-not-real')
@mock.patch('apps.core.keycrm_service.requests.put')
@mock.patch('apps.core.keycrm_service.requests.post')
class TzUpsellKeyCRMIdempotencyTests(TestCase):
    def _sub(self, card_id=None, age_seconds=0, **extra):
        data = {'pdf_token': TOKEN, 'site': 'cz', 'lang': 'cs'}
        data.update(extra)
        sub = FormSubmission.objects.create(
            form_type='tz_generator', name='TEST Jan', phone='+420777123456',
            email='test@example.com', extra_data=data,
            keycrm_card_id=card_id, keycrm_synced=bool(card_id),
        )
        if age_seconds:
            FormSubmission.objects.filter(pk=sub.pk).update(
                created_at=timezone.now() - timedelta(seconds=age_seconds))
            sub.refresh_from_db()
        return sub

    def _upsell(self, choice='estimate'):
        r = self.client.post(f'/forms/tz/{TOKEN}/upsell/', {'choice': choice})
        self.assertEqual(r.status_code, 200, r.content)
        self.assertTrue(json.loads(r.content)['success'])

    def test_upsell_updates_existing_card_not_creates(self, post, put):
        put.return_value = _resp(200)
        self._sub(card_id=101)
        self._upsell('estimate')
        post.assert_not_called()
        put.assert_called_once()
        url = put.call_args.args[0]
        self.assertTrue(url.endswith('/pipelines/cards/101'))
        self.assertEqual(put.call_args.kwargs['json'], {'note': '[Upsell] Хоче прорахунок'})

    def test_repeated_upsell_never_creates_second_card(self, post, put):
        put.return_value = _resp(200)
        self._sub(card_id=101)
        self._upsell('estimate')
        self._upsell('consultation')
        post.assert_not_called()
        self.assertEqual(put.call_count, 2)

    def test_fresh_submission_without_card_waits_for_dispatch(self, post, put):
        self._sub(card_id=None)
        self._upsell('consultation')
        post.assert_not_called()
        put.assert_not_called()

    def test_old_unsynced_submission_creates_once_then_updates(self, post, put):
        post.return_value = _resp(201, card_id=777)
        put.return_value = _resp(200)
        sub = self._sub(card_id=None, age_seconds=600)
        self._upsell('estimate')
        self.assertEqual(post.call_count, 1)
        sub.refresh_from_db()
        self.assertEqual(sub.keycrm_card_id, 777)
        self.assertIn('[Upsell]', post.call_args.kwargs['json']['manager_comment'])
        self._upsell('consultation')
        self.assertEqual(post.call_count, 1)
        put.assert_called_once()

    def test_sync_is_idempotent_when_card_exists(self, post, put):
        sub = self._sub(card_id=101)
        sync_submission_to_keycrm(sub)
        post.assert_not_called()

    def test_upsell_saved_during_create_is_pushed_via_update(self, post, put):
        post.return_value = _resp(201, card_id=888)
        put.return_value = _resp(200)
        sub = self._sub(card_id=None)  # в пам'яті без upsell
        FormSubmission.objects.filter(pk=sub.pk).update(
            extra_data={**sub.extra_data, 'upsell': 'consultation'})
        sync_submission_to_keycrm(sub)
        self.assertEqual(post.call_count, 1)
        put.assert_called_once()
        self.assertTrue(put.call_args.args[0].endswith('/pipelines/cards/888'))
        self.assertEqual(put.call_args.kwargs['json'], {'note': '[Upsell] Хоче консультацію'})

    def test_upsell_already_in_create_payload_no_extra_update(self, post, put):
        post.return_value = _resp(201, card_id=889)
        sub = self._sub(card_id=None, upsell='none')
        sync_submission_to_keycrm(sub)
        post.assert_called_once()
        put.assert_not_called()

    @override_settings(KEYCRM_API_KEY='')
    def test_unconfigured_sends_nothing(self, post, put):
        sub = self._sub(card_id=101)
        sync_tz_upsell_to_keycrm(sub)
        post.assert_not_called()
        put.assert_not_called()

    def test_put_failure_is_not_fatal(self, post, put):
        put.return_value = _resp(500)
        self._sub(card_id=101)
        self._upsell('estimate')
        post.assert_not_called()
