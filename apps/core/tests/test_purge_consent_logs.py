from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from apps.core.consent_models import ConsentLog


class PurgeConsentLogsTests(TestCase):
    def test_deletes_only_older_than_3_years(self):
        old = ConsentLog.objects.create(consent_id='a' * 16, action='accept_all')
        new = ConsentLog.objects.create(consent_id='b' * 16, action='reject_all')
        ConsentLog.objects.filter(pk=old.pk).update(created_at=timezone.now() - timedelta(days=3 * 365 + 1))
        ConsentLog.objects.filter(pk=new.pk).update(created_at=timezone.now() - timedelta(days=3 * 365 - 1))
        call_command('purge_consent_logs', stdout=StringIO())
        self.assertEqual(list(ConsentLog.objects.values_list('pk', flat=True)), [new.pk])

    def test_start_script_runs_purge(self):
        from pathlib import Path
        src = (Path(__file__).resolve().parents[3] / 'scripts/start.sh').read_text()
        self.assertIn('manage.py purge_consent_logs', src)
