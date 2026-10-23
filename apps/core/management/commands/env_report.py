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

        raw_key = settings.KEYCRM_API_KEY or ''
        if raw_key.strip():
            # Лише ознаки формату (без значення): чи є зайві пробіли/лапки/'Bearer '.
            stripped = raw_key.strip()
            flags = {
                'surrounding_whitespace': raw_key != stripped,
                'quotes': stripped[:1] in ('"', "'"),
                'bearer_prefix': stripped[:7].lower() == 'bearer ',
            }
            out('env_report: KEYCRM_API_KEY format: '
                + ' '.join(f'{k}={"yes" if v else "no"}' for k, v in flags.items()))
            from apps.core.keycrm_service import KeyCRMService
            ok, statuses, error = KeyCRMService().get_pipeline_statuses()
            if ok:
                out(f'env_report: KeyCRM pipeline {settings.KEYCRM_PIPELINE_ID} statuses (read-only):')
                for st in statuses:
                    out(f"  status id={st.get('id')} title={st.get('title') or st.get('name')}")
            else:
                out(f'env_report: KeyCRM statuses not available: {(error or "")[:120]}')

        self._smtp_check(out)

    def _smtp_check(self, out):
        """connect → STARTTLS → LOGIN → QUIT. Лист НЕ надсилається, значення не друкуються."""
        import smtplib

        if settings.EMAIL_BACKEND != 'django.core.mail.backends.smtp.EmailBackend':
            out(f'env_report: SMTP check skipped (backend {settings.EMAIL_BACKEND})')
            return
        stage = 'connect'
        try:
            conn = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
            try:
                conn.ehlo()
                if settings.EMAIL_USE_TLS:
                    stage = 'starttls'
                    conn.starttls()
                    conn.ehlo()
                stage = 'login'
                conn.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                out(f'env_report: SMTP check OK ({settings.EMAIL_HOST}:{settings.EMAIL_PORT} login accepted, no mail sent)')
            finally:
                try:
                    conn.quit()
                except Exception:
                    pass
        except Exception as exc:
            code = getattr(exc, 'smtp_code', '')
            out(f'env_report: SMTP check FAILED at {stage}: {exc.__class__.__name__}'
                f'{" " + str(code) if code else ""} ({settings.EMAIL_HOST}:{settings.EMAIL_PORT})')
