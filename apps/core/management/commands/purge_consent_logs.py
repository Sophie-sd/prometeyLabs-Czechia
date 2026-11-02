"""Delete cookie-consent audit records older than the retention period (default 3 years).

Retention is stated in /cookies/ and /privacy/ (CS/EN). Runs on every start (scripts/start.sh).
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.consent_models import ConsentLog

RETENTION_DAYS = 3 * 365


class Command(BaseCommand):
    help = 'Delete ConsentLog rows older than 3 years.'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=RETENTION_DAYS)
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **opts):
        cutoff = timezone.now() - timedelta(days=opts['days'])
        qs = ConsentLog.objects.filter(created_at__lt=cutoff)
        n = qs.count()
        if not opts['dry_run']:
            qs.delete()
        self.stdout.write(f"consent logs older than {cutoff:%Y-%m-%d}: {n}{' (dry run)' if opts['dry_run'] else ' deleted'}")
