"""#8: національний 0 після коду країни прибирається в payload KeyCRM."""
from unittest import mock

from django.test import SimpleTestCase, TestCase, override_settings

from apps.core.keycrm_service import KeyCRMService, normalize_phone_for_crm
from apps.core.models import FormSubmission


class NormalizePhoneTests(SimpleTestCase):
    def test_strips_trunk_zero(self):
        cases = {
            '+420 0777 123 456': '+420777123456',
            '+4200777123456': '+420777123456',
            '+420 (0) 777 123 456': '+420777123456',
            '+420(0)777123456': '+420777123456',
            '+421 0905 123 456': '+421905123456',
            '+380 099 123 45 67': '+380991234567',
            '+3800991234567': '+380991234567',
            '+44 07700 900123': '+447700900123',
            '+49-030-1234567': '+49301234567',
        }
        for raw, expected in cases.items():
            self.assertEqual(normalize_phone_for_crm(raw), expected, raw)

    def test_unchanged(self):
        for raw in ('+420 777 123 456', '+420777123456', '777 123 456', '0777123456',
                    '+39 06 1234 5678', '+420 702 012 345', '', '+44 0123'):
            self.assertEqual(normalize_phone_for_crm(raw), raw.strip(), raw)

    def test_no_separator_unknown_cc_untouched(self):
        # '+4207…' not '+42' + trunk 0; unknown CC without separator is ambiguous
        self.assertEqual(normalize_phone_for_crm('+4407700900123'), '+4407700900123')

    def test_none(self):
        self.assertEqual(normalize_phone_for_crm(None), '')


@override_settings(KEYCRM_API_KEY='test-key-not-real')
class KeycrmPayloadPhoneTests(TestCase):
    @mock.patch('apps.core.keycrm_service.requests.post')
    def test_payload_phone_normalized_submission_untouched(self, post):
        resp = mock.Mock(status_code=201, text='')
        resp.json.return_value = {'id': 1}
        post.return_value = resp
        sub = FormSubmission.objects.create(form_type='call_request', name='TEST Jan',
                                            phone='+420 0777 123 456', extra_data={})
        KeyCRMService().create_pipeline_card(sub)
        self.assertEqual(post.call_args.kwargs['json']['contact']['phone'], '+420777123456')
        sub.refresh_from_db()
        self.assertEqual(sub.phone, '+420 0777 123 456')
