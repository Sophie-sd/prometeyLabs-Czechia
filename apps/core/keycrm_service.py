"""
KeyCRM API інтеграція.
Створення карток воронки та отримання даних через OpenAPI.
"""
import requests
import logging
from django.conf import settings
from apps.core.form_handlers import get_answer_text, get_lead_site_code

logger = logging.getLogger(__name__)

KEYCRM_BASE_URL = 'https://openapi.keycrm.app/v1'
REQUEST_TIMEOUT = 15


def _to_int(value):
    """Безпечно конвертує env-значення у int. Порожній рядок або None → None."""
    if value in (None, ''):
        return None
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _split_tokens(raw):
    """'a,b , c' → ['a', 'b', 'c'] у нижньому регістрі без порожніх."""
    if not raw:
        return []
    return [t.strip().lower() for t in str(raw).split(',') if t.strip()]


def _campaign_matches(campaign, tokens):
    if not campaign or not tokens:
        return False
    campaign_lc = campaign.lower()
    return any(token in campaign_lc for token in tokens)


def _source_page(submission):
    extra = submission.extra_data or {}
    return (extra.get('source_page') or '').lower()


def _landing_page(submission):
    extra = submission.extra_data or {}
    return (extra.get('landing_page') or '').lower()


def _page_signals(submission):
    """Об'єднана підказка про сторінку: де залишена форма + куди вперше зайшов."""
    return f"{_source_page(submission)}|{_landing_page(submission)}"


def _has_any_utm(submission):
    """Чи є хоч один трекінг-параметр. gclid включено — Google Ads auto-tagging."""
    return any([
        submission.gclid,
        submission.utm_source,
        submission.utm_medium,
        submission.utm_campaign,
        submission.utm_term,
        submission.utm_content,
    ])


def resolve_keycrm_source_id(submission):
    """
    Обирає `source_id` для KeyCRM за пріоритетом:
    1. utm_source збігається з KEYCRM_UTM_MATCH_INSTAGRAM → KEYCRM_SOURCE_INSTAGRAM
    2. utm_campaign містить токени Shops               → KEYCRM_SOURCE_PAID_SHOPS
    3. utm_campaign містить токени Corporate            → KEYCRM_SOURCE_PAID_CORPORATE
    4. utm_campaign містить токени All                  → KEYCRM_SOURCE_PAID_ALL
    5. Немає жодного трекінг-параметра + корпоративна сторінка → KEYCRM_SOURCE_ORGANIC_CORPORATE
    6. Немає жодного трекінг-параметра + магазин               → KEYCRM_SOURCE_ORGANIC_SHOPS
    7. Fallback → KEYCRM_SOURCE_ID

    Повертає int або None, якщо нічого не сконфігуровано.
    """
    instagram = _to_int(getattr(settings, 'KEYCRM_SOURCE_INSTAGRAM', ''))
    paid_shops = _to_int(getattr(settings, 'KEYCRM_SOURCE_PAID_SHOPS', ''))
    paid_corporate = _to_int(getattr(settings, 'KEYCRM_SOURCE_PAID_CORPORATE', ''))
    paid_all = _to_int(getattr(settings, 'KEYCRM_SOURCE_PAID_ALL', ''))
    organic_shops = _to_int(getattr(settings, 'KEYCRM_SOURCE_ORGANIC_SHOPS', ''))
    organic_corporate = _to_int(getattr(settings, 'KEYCRM_SOURCE_ORGANIC_CORPORATE', ''))
    fallback = _to_int(getattr(settings, 'KEYCRM_SOURCE_ID', ''))

    utm_source = (submission.utm_source or '').strip().lower()
    campaign = (submission.utm_campaign or '').strip()

    # 1. Instagram
    ig_tokens = _split_tokens(getattr(settings, 'KEYCRM_UTM_MATCH_INSTAGRAM', ''))
    if utm_source and ig_tokens and utm_source in ig_tokens:
        return instagram or fallback

    # 2–4. utm_campaign токени
    if _campaign_matches(campaign, _split_tokens(getattr(settings, 'KEYCRM_UTM_MATCH_PAID_SHOPS', ''))) and paid_shops:
        return paid_shops
    if _campaign_matches(campaign, _split_tokens(getattr(settings, 'KEYCRM_UTM_MATCH_PAID_CORPORATE', ''))) and paid_corporate:
        return paid_corporate
    if _campaign_matches(campaign, _split_tokens(getattr(settings, 'KEYCRM_UTM_MATCH_PAID_ALL', ''))) and paid_all:
        return paid_all

    # 5–6. Немає жодного трекінг-параметра → органіка за сторінкою
    if not _has_any_utm(submission):
        page = _page_signals(submission)
        if 'corporate-website' in page and organic_corporate:
            return organic_corporate
        if 'internet-shop' in page and organic_shops:
            return organic_shops

    return fallback


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
                'phone': submission.phone,
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
        comment_parts.append(f'Form: {submission.form_type}')
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
        extra = submission.extra_data or {}
        if extra.get('source_page'):
            comment_parts.append(f'Сторінка заявки: {extra["source_page"]}')
        if extra.get('landing_page'):
            comment_parts.append(f'Перша сторінка: {extra["landing_page"]}')
        if extra.get('landing_referrer'):
            comment_parts.append(f'Реферер: {extra["landing_referrer"]}')
        if submission.gclid:
            comment_parts.append(f'GCLID: {submission.gclid}')

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


def sync_submission_to_keycrm(submission):
    """
    Хелпер: синхронізує FormSubmission з KeyCRM.
    Оновлює keycrm_card_id та keycrm_synced на submission.
    """
    service = KeyCRMService()
    if not service.is_configured:
        return

    success, card_id, error = service.create_pipeline_card(submission)

    if success and card_id:
        submission.keycrm_card_id = card_id
        submission.keycrm_synced = True
        submission.save(update_fields=['keycrm_card_id', 'keycrm_synced'])
        logger.info(f"Submission {submission.id} synced to KeyCRM card {card_id}")
    elif error:
        logger.error(f"Failed to sync submission {submission.id} to KeyCRM: {error}")
