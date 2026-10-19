"""Сторінка /tz-dlia-saitu/ — генератор базового ТЗ + PDF."""
from __future__ import annotations

import json
import logging
import re
import secrets

from django.http import HttpResponse, JsonResponse
from django.utils import timezone, translation
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _lazy
from django.views.decorators.http import require_POST, require_GET

from apps.core.form_handlers import (
    create_form_data,
    create_form_response,
    has_consent,
    save_form_submission,
    validate_name,
    validate_phone,
)
from apps.core.mixins import BasePageView
from apps.core.views import _dispatch_async

logger = logging.getLogger(__name__)

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


class TzGeneratorView(BasePageView):
    """Landing: створити ТЗ для сайту — інтерактивний квіз + PDF."""

    template_name = 'pages/tz-dlia-saitu.html'
    page_title = _lazy(
        'Створити ТЗ для сайту безкоштовно за 3 хвилини | PrometeyLabs'
    )
    meta_description = _lazy(
        'Як правильно скласти ТЗ для сайту: інтерактивний конструктор. '
        'Отримайте базове технічне завдання в PDF одразу та розширене — на email протягом доби.'
    )
    og_title = _lazy('Створити ТЗ для сайту онлайн — безкоштовно | PrometeyLabs')
    keywords = _lazy(
        'створити ТЗ для сайту, технічне завдання для сайту, як скласти ТЗ, '
        'бриф на розробку сайту, ТЗ на лендінг, ТЗ інтернет-магазин'
    )


def _parse_quiz(raw: str) -> dict:
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except (TypeError, ValueError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _validate_email(email: str) -> bool:
    return bool(email and EMAIL_RE.match(email) and len(email) <= 254)


@require_POST
def handle_tz_submission(request):
    """POST /forms/tz/ — контакт-гейт після квіза → PDF token."""
    name = request.POST.get('name', '').strip()
    phone = request.POST.get('phone', '').strip()
    email = request.POST.get('email', '').strip()
    quiz = _parse_quiz(request.POST.get('quiz', ''))

    # GDPR: серверна перевірка згоди (фронт шле consent=1, як інші lead-форми)
    if not has_consent(request):
        return create_form_response(
            False,
            _('Підтвердіть згоду на обробку персональних даних.'),
            status=400,
        )
    if not name or not phone or not email:
        return create_form_response(
            False,
            _('Заповніть імʼя, телефон і email'),
        )
    if not validate_name(name):
        return create_form_response(False, _('Введіть коректне імʼя'))
    if not validate_phone(phone):
        return create_form_response(False, _('Введіть коректний номер телефону'))
    if not _validate_email(email):
        return create_form_response(False, _('Введіть коректний email'))

    token = secrets.token_urlsafe(24)
    details_parts = []
    if quiz.get('description'):
        details_parts.append(str(quiz['description'])[:2000])
    if quiz.get('extra'):
        details_parts.append(str(quiz['extra'])[:1000])

    form_data = create_form_data(
        _('Генератор ТЗ для сайту'),
        name,
        phone,
        request,
        email=email,
        details='\n\n'.join(details_parts),
        quiz=quiz,
        pdf_token=token,
        source_page='tz-dlia-saitu',
    )

    saved, submission_id, save_error = save_form_submission(
        'tz_generator', form_data, email_success=False
    )
    if not saved:
        logger.error('TZ submit save failed: %s', save_error)
        return create_form_response(
            False,
            _('Помилка при збереженні. Спробуйте ще раз.'),
        )

    _dispatch_async(submission_id, form_data)

    from django.urls import reverse

    pdf_url = reverse('tz_pdf', kwargs={'token': token})
    return create_form_response(
        True,
        _('Базове ТЗ готове. Завантажте PDF — розширене надійде на пошту протягом доби.'),
        pdf_url=pdf_url,
        token=token,
        submission_id=submission_id,
    )


TZ_PDF_FILENAMES = {
    'cs': 'Zadani-webu.pdf',
    'en': 'Website-brief.pdf',
}


def tz_pdf_filename(submission=None) -> str:
    """Ім'я PDF за мовою: мова ліда (extra_data.lang) → активна мова → cs."""
    lang = ((submission.extra_data or {}).get('lang') if submission is not None else '') or ''
    lang = (lang or translation.get_language() or 'cs').split('-')[0].lower()
    return TZ_PDF_FILENAMES.get(lang, TZ_PDF_FILENAMES['cs'])


@require_GET
def download_tz_pdf(request, token: str):
    """GET /forms/tz/<token>/pdf/ — миттєвий PDF з базовим ТЗ."""
    from apps.core.models import FormSubmission
    from apps.core.tz_pdf import generate_tz_pdf_bytes

    submission = (
        FormSubmission.objects
        .filter(form_type='tz_generator', extra_data__pdf_token=token)
        .order_by('-created_at')
        .first()
    )
    if not submission:
        return JsonResponse({'success': False, 'message': _('ТЗ не знайдено')}, status=404)

    try:
        pdf_bytes = generate_tz_pdf_bytes(submission)
    except Exception as exc:
        logger.error('TZ PDF error for %s: %s', submission.id, exc)
        return JsonResponse(
            {'success': False, 'message': _('Не вдалося згенерувати PDF')},
            status=500,
        )

    filename = tz_pdf_filename(submission)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response['Cache-Control'] = 'private, no-store'
    return response


@require_POST
def handle_tz_upsell(request, token: str):
    """POST /forms/tz/<token>/upsell/ — прорахунок або консультація після PDF."""
    from apps.core.models import FormSubmission

    choice = request.POST.get('choice', '').strip()
    if choice not in {'estimate', 'consultation', 'none'}:
        return create_form_response(False, _('Невірний вибір'))

    submission = (
        FormSubmission.objects
        .filter(form_type='tz_generator', extra_data__pdf_token=token)
        .order_by('-created_at')
        .first()
    )
    if not submission:
        return create_form_response(False, _('Заявку не знайдено'))

    extra = dict(submission.extra_data or {})
    extra['upsell'] = choice
    extra['upsell_at'] = timezone.now().isoformat()
    submission.extra_data = extra

    labels = {
        'estimate': _('Хоче прорахунок'),
        'consultation': _('Хоче консультацію'),
        'none': _('Без додаткових послуг'),
    }
    note = f"\n\n[Upsell] {labels[choice]}"
    submission.details = (submission.details or '') + note
    if choice == 'estimate':
        submission.priority = 'high'
    submission.save(update_fields=['extra_data', 'details', 'priority'])

    try:
        # Оновлюємо існуючу картку, а не створюємо другу (idempotent upsell).
        from apps.core.keycrm_service import sync_tz_upsell_to_keycrm
        sync_tz_upsell_to_keycrm(submission)
    except Exception as exc:
        logger.warning('TZ upsell KeyCRM: %s', exc)

    messages = {
        'estimate': _('Дякуємо! Підготуємо прорахунок і напишемо вам.'),
        'consultation': _('Дякуємо! Менеджер звʼяжеться для консультації.'),
        'none': _('Добре. Базове ТЗ у PDF, розширене — на email протягом доби.'),
    }
    return create_form_response(True, messages[choice], choice=choice)
