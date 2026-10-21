"""
KeyCRM API інтеграція.
Створення карток воронки та отримання даних через OpenAPI.
"""
import re
import requests
import logging
from django.conf import settings
from apps.core.form_handlers import (
    get_answer_text, get_lead_site_code, get_lead_source_domain, page_language_label,
)

logger = logging.getLogger(__name__)

KEYCRM_BASE_URL = 'https://openapi.keycrm.app/v1'
REQUEST_TIMEOUT = 15


# #8: зайвий національний 0 після коду країни ('+420 0777…' → '+420777…').
# Без роздільника — лише для кодів, де національний номер ніколи не починається з 0.
_TRUNK_ZERO_SAFE_CC = ('420', '421', '380')
# Італія / Сан-Марино / Ватикан: 0 — частина номера, не чіпаємо.
_TRUNK_ZERO_KEEP_CC = {'39', '378', '379'}
_PHONE_TRUNK_SEP_RE = re.compile(
    r'^\+(\d{1,3})(?:[\s.\-/]+\(?0\)?|\(0\))[\s.\-/]*(\d[\d\s.\-/()]*)$'
)
_PHONE_TRUNK_NOSEP_RE = re.compile(
    r'^\+(' + '|'.join(_TRUNK_ZERO_SAFE_CC) + r')0(\d[\d\s.\-/()]*)$'
)


def normalize_phone_for_crm(phone):
    """Мінімальна нормалізація для KeyCRM: прибирає національний 0 після +код.
    Якщо шаблон не збігся — номер повертається без змін."""
    raw = (phone or '').strip()
    match = _PHONE_TRUNK_SEP_RE.match(raw) or _PHONE_TRUNK_NOSEP_RE.match(raw)
    if not match or match.group(1) in _TRUNK_ZERO_KEEP_CC:
        return raw
    rest = re.sub(r'\D', '', match.group(2))
    if len(match.group(1) + rest) < 7:
        return raw
    return f'+{match.group(1)}{rest}'


def _to_int(value):
    """Безпечно конвертує env-значення у int. Порожній рядок або None → None."""
    if value in (None, ''):
        return None
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def resolve_keycrm_source_id(submission):
    """
    source_id для CZ-ліда (перше правило, що спрацювало):
    1. є gclid і utm_campaign == 'cz_eshopy'                   → KEYCRM_SOURCE_CZ_ESHOPY (13)
    2. є gclid (кампанія 'cz_general', порожня або невідома)   → KEYCRM_SOURCE_CZ_GENERAL (12)
    3. gclid немає                                             → KEYCRM_SOURCE_CZ_ORGANIC (14)
    Значення 15 сайт не ставить ніколи. Порівняння кампанії — без регістру та пробілів.
    """
    gclid = (submission.gclid or '').strip()
    campaign = (submission.utm_campaign or '').strip().lower()
    eshopy = (getattr(settings, 'KEYCRM_CAMPAIGN_CZ_ESHOPY', 'cz_eshopy') or 'cz_eshopy').strip().lower()
    if gclid and campaign == eshopy:
        source = _to_int(getattr(settings, 'KEYCRM_SOURCE_CZ_ESHOPY', 13))
    elif gclid:
        source = _to_int(getattr(settings, 'KEYCRM_SOURCE_CZ_GENERAL', 12))
    else:
        source = _to_int(getattr(settings, 'KEYCRM_SOURCE_CZ_ORGANIC', 14))
    if source == 15:  # захист: 15 виставляється лише вручну в CRM
        return None
    return source


def lead_site_and_lang(submission):
    """
    (site, lang) для заявки: з extra_data (пишеться в create_form_data),
    інакше site — з налаштування, lang — preferred_language або ''.
    """
    extra = submission.extra_data or {}
    site = (extra.get('site') or get_lead_site_code() or '').strip().lower()
    lang = (extra.get('lang') or submission.preferred_language or '').strip().lower()
    return site, lang


class KeyCRMService:
    def __init__(self):
        self.api_key = getattr(settings, 'KEYCRM_API_KEY', '')
        self.pipeline_id = getattr(settings, 'KEYCRM_PIPELINE_ID', 1)
        self.gclid_field_uuid = getattr(settings, 'KEYCRM_GCLID_FIELD_UUID', '')
        # Опційні кастомні поля картки (UUID з KeyCRM). Порожньо → лише manager_comment.
        self.site_field_uuid = getattr(settings, 'KEYCRM_SITE_FIELD_UUID', '')
        self.lang_field_uuid = getattr(settings, 'KEYCRM_LANG_FIELD_UUID', '')

    @property
    def _headers(self):
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    @property
    def is_configured(self):
        return bool(self.api_key)

    def create_pipeline_card(self, submission):
        """
        Створює картку у воронці KeyCRM з даних FormSubmission.
        Повертає (success: bool, card_id: int|None, error: str|None)
        """
        if not self.is_configured:
            logger.warning("KeyCRM API key not configured, skipping")
            return (False, None, "API key not configured")

        payload = {
            'pipeline_id': self.pipeline_id,
            'title': f'{submission.get_form_type_display()} - {submission.name}',
            'contact': {
                'full_name': submission.name,
                'phone': normalize_phone_for_crm(submission.phone),
            },
        }

        if submission.email:
            payload['contact']['email'] = submission.email

        source_id = resolve_keycrm_source_id(submission)
        if source_id:
            payload['source_id'] = source_id

        if submission.utm_source:
            payload['utm_source'] = submission.utm_source
        if submission.utm_medium:
            payload['utm_medium'] = submission.utm_medium
        if submission.utm_campaign:
            payload['utm_campaign'] = submission.utm_campaign
        if submission.utm_term:
            payload['utm_term'] = submission.utm_term
        if submission.utm_content:
            payload['utm_content'] = submission.utm_content

        site, lang = lead_site_and_lang(submission)

        custom_fields = []
        if submission.gclid and self.gclid_field_uuid:
            custom_fields.append({
                'uuid': self.gclid_field_uuid,
                'value': submission.gclid,
            })
        if site and self.site_field_uuid:
            custom_fields.append({'uuid': self.site_field_uuid, 'value': site})
        if lang and self.lang_field_uuid:
            custom_fields.append({'uuid': self.lang_field_uuid, 'value': lang})
        if custom_fields:
            payload['custom_fields'] = custom_fields

        comment_parts = []
        if submission.details:
            comment_parts.append(submission.details)
        extra = submission.extra_data or {}
        comment_parts.append(f'Source: {get_lead_source_domain()}')
        comment_parts.append(f'Page language: {page_language_label(lang) or "-"}')
        comment_parts.append(f'Form: {submission.form_type}')
        # Сирі значення атрибуції (п.3 ТЗ) — завжди всі ключі, порожні як '-'.
        tracking = [
            ('form_type', submission.form_type),
            ('page_language', page_language_label(lang)),
            ('gclid', submission.gclid),
            ('utm_source', submission.utm_source),
            ('utm_medium', submission.utm_medium),
            ('utm_campaign', submission.utm_campaign),
            ('utm_term', submission.utm_term),
            ('utm_content', submission.utm_content),
            ('landing_referrer', extra.get('landing_referrer')),
            ('landing_page', extra.get('landing_page')),
            ('source_page', extra.get('source_page')),
        ]
        comment_parts.append(
            '=== TRACKING ===\n' + '\n'.join(f'{k}: {v or "-"}' for k, v in tracking)
        )
        if site:
            comment_parts.append(f'Site: {site}')
        if lang:
            comment_parts.append(f'Lang: {lang}')
        comment_parts.append(f'Site ID: {submission.id}')
        if submission.messenger_type:
            comment_parts.append(
                f'Messenger: {submission.get_messenger_type_display()}'
            )
        if submission.project_type:
            comment_parts.append(
                f'Project type: {submission.get_project_type_display()}'
            )
        if submission.budget:
            comment_parts.append(f'Budget: {submission.get_budget_display()}')
        if submission.preferred_language:
            comment_parts.append(
                f'Preferred language: {submission.get_preferred_language_display()}'
            )
        if submission.gclid:
            comment_parts.append(f'GCLID: {submission.gclid}')
        if extra.get('quiz_answers'):
            from apps.core.quiz_options import format_quiz_answers
            quiz_lines = format_quiz_answers(extra['quiz_answers'])
            if quiz_lines:
                comment_parts.append('=== КВІЗ ===\n' + '\n'.join(quiz_lines))

        if submission.form_type == 'test_result' and submission.extra_data:
            extra = submission.extra_data
            answers = extra.get('answers', {})
            alt_checked = extra.get('alt_services_checked', False)

            if alt_checked and answers:
                comment_parts.append('Галочка: Так\nТест: Пройдений')
            elif alt_checked:
                comment_parts.append('Галочка: Так\nТест: Не пройдений')
            elif answers:
                comment_parts.append('Галочка: Ні\nТест: Пройдений')

            if answers:
                lines = ['=== ВІДПОВІДІ НА ТЕСТ ===']
                for i in range(1, 6):
                    key = f'question_{i}'
                    if key in answers:
                        lines.append(f'{i}. {get_answer_text(key, answers[key])}')
                comment_parts.append('\n'.join(lines))

        payload['manager_comment'] = '\n'.join(comment_parts)

        try:
            response = requests.post(
                f'{KEYCRM_BASE_URL}/pipelines/cards',
                json=payload,
                headers=self._headers,
                timeout=REQUEST_TIMEOUT,
            )

            if response.status_code in (200, 201):
                data = response.json()
                card_id = data.get('id')
                logger.info(f"KeyCRM card created: {card_id} for submission {submission.id}")
                return (True, card_id, None)
            else:
                error = f"KeyCRM API error {response.status_code}: {response.text[:300]}"
                logger.error(error)
                return (False, None, error)

        except requests.Timeout:
            error = "KeyCRM API timeout"
            logger.error(error)
            return (False, None, error)
        except requests.RequestException as e:
            error = f"KeyCRM API request failed: {str(e)}"
            logger.error(error)
            return (False, None, error)

    def get_pipeline_statuses(self, pipeline_id=None):
        """GET /pipelines/{id}/statuses → (success, [ {id, title/name, ...} ], error). Read-only."""
        if not self.is_configured:
            return (False, [], "API key not configured")
        pid = pipeline_id or self.pipeline_id
        try:
            response = requests.get(
                f'{KEYCRM_BASE_URL}/pipelines/{pid}/statuses',
                params={'limit': 50},
                headers=self._headers,
                timeout=REQUEST_TIMEOUT,
            )
            if response.status_code == 200:
                return (True, response.json().get('data') or [], None)
            return (False, [], f"KeyCRM statuses error {response.status_code}: {response.text[:300]}")
        except requests.RequestException as e:
            return (False, [], f"KeyCRM statuses request failed: {e}")

    def update_pipeline_card(self, card_id, payload):
        """
        Оновлює існуючу картку: PUT /pipelines/cards/{cardId}
        (поля title, note, status_id, source_id, custom_fields — див. open-api.yml).
        Повертає (success: bool, error: str|None).
        """
        if not self.is_configured:
            return (False, "API key not configured")
        if not card_id:
            return (False, "No card id")

        try:
            response = requests.put(
                f'{KEYCRM_BASE_URL}/pipelines/cards/{card_id}',
                json=payload,
                headers=self._headers,
                timeout=REQUEST_TIMEOUT,
            )
            if response.status_code in (200, 201):
                logger.info(f"KeyCRM card updated: {card_id}")
                return (True, None)
            error = f"KeyCRM PUT card error {response.status_code}: {response.text[:300]}"
            logger.error(error)
            return (False, error)
        except requests.Timeout:
            error = "KeyCRM API timeout (update)"
            logger.error(error)
            return (False, error)
        except requests.RequestException as e:
            error = f"KeyCRM API update failed: {str(e)}"
            logger.error(error)
            return (False, error)

    def get_card_with_custom_fields(self, card_id):
        """
        Отримує картку воронки з кастомними полями.
        Повертає (success, data_dict|None, error)
        """
        if not self.is_configured:
            return (False, None, "API key not configured")

        try:
            response = requests.get(
                f'{KEYCRM_BASE_URL}/pipelines/cards/{card_id}',
                params={'include': 'custom_fields'},
                headers=self._headers,
                timeout=REQUEST_TIMEOUT,
            )

            if response.status_code == 200:
                return (True, response.json(), None)
            else:
                error = f"KeyCRM GET card error {response.status_code}: {response.text[:300]}"
                logger.error(error)
                return (False, None, error)

        except requests.RequestException as e:
            error = f"KeyCRM GET card failed: {str(e)}"
            logger.error(error)
            return (False, None, error)

    def extract_gclid_from_card(self, card_data):
        """Витягує GCLID з кастомних полів картки."""
        custom_fields = card_data.get('custom_fields', [])
        if not custom_fields:
            return None

        for field in custom_fields:
            if field.get('uuid') == self.gclid_field_uuid:
                return field.get('value')

        for field in custom_fields:
            name = (field.get('name') or '').lower()
            if 'gclid' in name:
                return field.get('value')

        return None


UPSELL_NOTE_LABELS = {
    'estimate': 'Хоче прорахунок',
    'consultation': 'Хоче консультацію',
    'none': 'Без додаткових послуг',
}

# Скільки секунд після створення заявки вважаємо, що фонова відправка
# (_dispatch_async: e-mail до 10 с + KeyCRM до 15 с) ще може створити картку.
KEYCRM_PENDING_CREATE_SECONDS = 60


def _upsell_note(upsell):
    label = UPSELL_NOTE_LABELS.get(upsell, upsell)
    return f'[Upsell] {label}'


def sync_submission_to_keycrm(submission):
    """
    Хелпер: синхронізує FormSubmission з KeyCRM (створює картку).
    Оновлює keycrm_card_id та keycrm_synced на submission.

    Ідемпотентний: якщо в заявки вже є keycrm_card_id — нову картку не створює.
    Якщо поки картка створювалась, у заявку додали upsell (tz-generator),
    після створення доливаємо його в картку через update.
    """
    service = KeyCRMService()
    if not service.is_configured:
        return

    if submission.keycrm_card_id:
        logger.info(
            f"Submission {submission.id} already has KeyCRM card "
            f"{submission.keycrm_card_id}; skip create"
        )
        return

    upsell_at_create = (submission.extra_data or {}).get('upsell')
    success, card_id, error = service.create_pipeline_card(submission)

    if success and card_id:
        submission.keycrm_card_id = card_id
        submission.keycrm_synced = True
        submission.save(update_fields=['keycrm_card_id', 'keycrm_synced'])
        logger.info(f"Submission {submission.id} synced to KeyCRM card {card_id}")

        # POST не приймає status_id → картка в першому статусі воронки («Новий»).
        # Якщо статус «Новий» не перший — KEYCRM_NEW_STATUS_ID + PUT.
        new_status = _to_int(getattr(settings, 'KEYCRM_NEW_STATUS_ID', ''))
        if new_status:
            service.update_pipeline_card(card_id, {'status_id': new_status})

        try:
            fresh_upsell = (
                type(submission).objects.filter(pk=submission.pk)
                .values_list('extra_data', flat=True).first() or {}
            ).get('upsell')
        except Exception:  # pragma: no cover — захисно, не валимо фонову відправку
            fresh_upsell = None
        if fresh_upsell and fresh_upsell != upsell_at_create:
            service.update_pipeline_card(card_id, {'note': _upsell_note(fresh_upsell)})
    elif error:
        logger.error(f"Failed to sync submission {submission.id} to KeyCRM: {error}")


def sync_tz_upsell_to_keycrm(submission):
    """
    Upsell після генератора ТЗ: оновлює існуючу картку, а не створює другу.

    - є keycrm_card_id → PUT note з upsell;
    - картки ще немає, а заявка свіжа → нічого не робимо: фонова відправка
      створить картку з уже збереженим upsell (або доллє його після створення);
    - картки немає і заявка стара (первинна відправка не вдалась) → створюємо.
    """
    from django.utils import timezone

    service = KeyCRMService()
    if not service.is_configured:
        return

    submission.refresh_from_db(fields=['keycrm_card_id', 'keycrm_synced', 'extra_data', 'created_at'])
    upsell = (submission.extra_data or {}).get('upsell')

    if submission.keycrm_card_id:
        if upsell:
            service.update_pipeline_card(submission.keycrm_card_id, {'note': _upsell_note(upsell)})
        return

    age = (timezone.now() - submission.created_at).total_seconds() if submission.created_at else None
    if age is not None and age < KEYCRM_PENDING_CREATE_SECONDS:
        logger.info(
            f"Submission {submission.id}: KeyCRM card creation pending; upsell will be included"
        )
        return

    sync_submission_to_keycrm(submission)
