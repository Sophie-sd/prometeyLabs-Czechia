"""Згода на чекаут: чекбокси, IP, лист-підтвердження (§1824a NOZ)."""
import logging

from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.utils import translation

from .amount_words import format_money
from .models import PaymentLink
from .texts import current_lang, get_texts, normalize_lang

logger = logging.getLogger('payment')

_CHECKED = frozenset({'1', 'on', 'true', 'yes'})


def client_ip(request: HttpRequest):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[0].strip() or None
    return request.META.get('REMOTE_ADDR') or None


def has_checkout_consents(request: HttpRequest) -> bool:
    waiver = (request.POST.get('withdrawal_waiver') or '').strip().lower()
    consent = (request.POST.get('data_consent') or '').strip().lower()
    return waiver in _CHECKED and consent in _CHECKED


def require_and_record_consents(request: HttpRequest, payment_link: PaymentLink):
    """400, якщо чекбокси не відмічені; інакше фіксує час і IP."""
    if not has_checkout_consents(request):
        return HttpResponseBadRequest(
            get_texts(current_lang())['consent_error'],
            content_type='text/plain; charset=utf-8',
        )
    payment_link.record_checkout_consent(client_ip(request))
    return None


def send_payment_confirmation(payment_link: PaymentLink):
    """Лист клієнту з текстом про втрату права відступлення. Без ODR."""
    email = (payment_link.client_email or '').strip()
    if not email:
        return
    lang = normalize_lang(payment_link.language)
    texts = get_texts(lang)
    try:
        with translation.override(lang):
            body = render_to_string('payment/emails/payment_confirmation.txt', {
                'payment_link': payment_link,
                't': texts,
                'amount_display': format_money(payment_link.amount, lang),
                'show_currency': not payment_link.is_legacy_currency,
            })
        send_mail(
            subject=texts['email_subject'],
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception:
        logger.exception(
            'Payment confirmation email failed: link=%s',
            payment_link.unique_id,
        )
