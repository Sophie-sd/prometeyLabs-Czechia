"""Діагностика конфігурації для build-логу Render БЕЗ секретів.

Секрети — лише set/not set. Несекретні значення (EMAIL_HOST, порт, бекенд, pipeline,
UUID поля) — як є. Якщо KEYCRM_API_KEY задано — read-only GET статусів воронки
(нічого не створює). Ніколи не падає (не ламає деплой).
"""
import os

from django.conf import settings
from django.core.management.base import BaseCommand

SECRET_PRESENCE = (
    'KEYCRM_API_KEY', 'EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD', 'DEFAULT_FROM_EMAIL',
    'CONTACT_EMAIL', 'MAILGUN_API_KEY', 'KEYCRM_PIPELINE_ID', 'KEYCRM_GCLID_FIELD_UUID',
    'KEYCRM_NEW_STATUS_ID', 'KEYCRM_SOURCE_ID', 'COOKIEYES_ID',
)


class Command(BaseCommand):
    help = 'Друкує, які env задані (yes/no) і несекретні налаштування пошти/KeyCRM'

    def handle(self, *args, **options):
        try:
            self._report()
        except Exception as exc:  # pragma: no cover — діагностика не має ламати build
            self.stdout.write(f'env_report: failed: {exc.__class__.__name__}')

    def _report(self):
        out = self.stdout.write
        out('env_report: env presence (yes/no, values hidden):')
        for key in SECRET_PRESENCE:
            out(f'  {key}={"yes" if (os.environ.get(key) or "").strip() else "no"}')
        out('env_report: effective non-secret settings:')
        out(f'  EMAIL_BACKEND={settings.EMAIL_BACKEND}')
        out(f'  EMAIL_HOST={settings.EMAIL_HOST}')
        out(f'  EMAIL_PORT={settings.EMAIL_PORT}')
        out(f'  EMAIL_USE_TLS={getattr(settings, "EMAIL_USE_TLS", "")}')
        from_domain = (settings.DEFAULT_FROM_EMAIL or '').rsplit('@', 1)[-1].strip('> ')
        out(f'  DEFAULT_FROM_EMAIL domain={from_domain}')
        out(f'  KEYCRM_PIPELINE_ID={settings.KEYCRM_PIPELINE_ID}')
        out(f'  KEYCRM_GCLID_FIELD_UUID={settings.KEYCRM_GCLID_FIELD_UUID}')
        out(f'  KEYCRM_NEW_STATUS_ID={settings.KEYCRM_NEW_STATUS_ID or "(empty -> first status of pipeline)"}')
        out(f'  KEYCRM_SOURCE_CZ (eshopy/general/organic)='
            f'{settings.KEYCRM_SOURCE_CZ_ESHOPY}/{settings.KEYCRM_SOURCE_CZ_GENERAL}/{settings.KEYCRM_SOURCE_CZ_ORGANIC}')

        if (settings.KEYCRM_API_KEY or '').strip():
            from apps.core.keycrm_service import KeyCRMService
            ok, statuses, error = KeyCRMService().get_pipeline_statuses()
            if ok:
                out(f'env_report: KeyCRM pipeline {settings.KEYCRM_PIPELINE_ID} statuses (read-only):')
                for st in statuses:
                    out(f"  status id={st.get('id')} title={st.get('title') or st.get('name')}")
            else:
                out(f'env_report: KeyCRM statuses not available: {(error or "")[:120]}')
