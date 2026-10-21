"""Read-only: друкує статуси воронки KeyCRM (id + назва), щоб знайти ID статусу «Новий».

    python manage.py keycrm_pipeline_statuses            # воронка KEYCRM_PIPELINE_ID (6)
    python manage.py keycrm_pipeline_statuses --pipeline 6
Потрібен KEYCRM_API_KEY у середовищі. Нічого не створює і не змінює.
"""
from django.core.management.base import BaseCommand

from apps.core.keycrm_service import KeyCRMService


class Command(BaseCommand):
    help = 'Показати статуси воронки KeyCRM (read-only)'

    def add_arguments(self, parser):
        parser.add_argument('--pipeline', type=int, default=None)

    def handle(self, *args, **options):
        service = KeyCRMService()
        ok, statuses, error = service.get_pipeline_statuses(options.get('pipeline'))
        if not ok:
            self.stdout.write(self.style.WARNING(f'keycrm_pipeline_statuses: {error}'))
            return
        for st in statuses:
            name = st.get('title') or st.get('name') or ''
            self.stdout.write(f"{st.get('id')}\t{name}\t(alias={st.get('alias', '')}, group={st.get('group_id', '')})")
