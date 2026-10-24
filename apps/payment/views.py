import json
import logging
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import List

from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.utils import timezone, translation
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe
from django.urls import reverse

from .amount_words import format_money, plain_amount
from .checkout import (
    has_checkout_consents,
    require_and_record_consents,
    send_payment_confirmation,
)
from .models import PaymentLink, PaymentSettings, SubscriptionCharge, method_public_block
from .monobank_service import MonobankAcquiringService
from .subscription_service import MonobankSubscriptionService
from .texts import current_lang, get_texts

logger = logging.getLogger('payment')

PAYMENT_SETTINGS_CACHE_KEY = 'payment_settings'
PAYMENT_SETTINGS_CACHE_TTL = 3600


def get_payment_settings():
    """Cached PaymentSettings lookup. Cache is invalidated via signal on save."""
    settings = cache.get(PAYMENT_SETTINGS_CACHE_KEY)
    if settings is None:
        settings = PaymentSettings.objects.first()
        cache.set(PAYMENT_SETTINGS_CACHE_KEY, settings, PAYMENT_SETTINGS_CACHE_TTL)
    return settings


def _status_context(request: HttpRequest, extra: dict | None = None) -> dict:
    lang = current_lang()
    ctx = {'t': get_texts(lang), 'lang': lang}
    ctx.update(extra or {})
    return ctx


def _render_inactive(request: HttpRequest, payment_link: PaymentLink):
    return render(request, 'payment/link_inactive.html', _status_context(request, {
        'payment_link': payment_link,
        'is_paid': payment_link.status == PaymentLink.Status.PAID,
    }))


def _method_copy_payload(block: dict, texts: dict, purpose: str, amount_line: str) -> List[str]:
    """Текст для кнопки «Kopírovat údaje SEPA / Copy SWIFT details»."""
    # Same order as on the page: amount, purpose, then the method details.
    lines = [f"{texts['field_amount']}: {amount_line}"]
    if purpose:
        lines.append(f"{texts['field_purpose']}: {purpose}")
    lines += [f"{row['label']}: {row['value']}" for row in block['rows']]
    if block.get('paypal_url'):
        lines.append(block['paypal_url'])
    return lines


def build_payment_blocks(payment_link: PaymentLink, texts: dict, lang: str) -> list:
    purpose = payment_link.payment_purpose()
    amount_line = f'{plain_amount(payment_link.amount)} {payment_link.currency}'
    blocks = []
    for idx, method in enumerate(
        payment_link.payment_methods.filter(is_active=True, currency=payment_link.currency).order_by('position', 'name'),
        start=1,
    ):
        block = method_public_block(method.snapshot(), texts, lang)
        block['dom_id'] = f'pay-method-{idx}'
        block['copy_payload'] = _method_copy_payload(block, texts, purpose, amount_line)
        block['copy_label'] = texts['copy_details'].replace('{method}', block['short_label'])
        blocks.append(block)
    return blocks


def _next_month_first(from_date: date) -> date:
    """Returns the 1st day of the month following from_date."""
    if from_date.month == 12:
        return from_date.replace(year=from_date.year + 1, month=1, day=1)
    return from_date.replace(month=from_date.month + 1, day=1)


def _card_token_from_wallet_cards(cards: list) -> str:
    """Picks cardToken from Monobank wallet cards list (active card preferred)."""
    if not cards:
        return ''
    active = next((c for c in cards if c.get('status') == 'active'), None)
    return (active or {}).get('cardToken', '') or ''


def _activate_subscription(payment_link: PaymentLink, payload: dict) -> None:
    """Called from webhook after first subscription payment succeeds."""
    invoice_sub = payload.get('invoice') if isinstance(payload.get('invoice'), dict) else {}
    wallet_data = payload.get('walletData') or invoice_sub.get('walletData') or {}
    card_token = wallet_data.get('cardToken', '')

    if not card_token:
        logger.warning(
            'No cardToken in webhook payload for %s. Payload: %s',
            payment_link.unique_id,
            payload,
        )
        svc = MonobankSubscriptionService()
        cards = svc.get_wallet_cards(str(payment_link.unique_id)) or []
        card_token = _card_token_from_wallet_cards(cards)

    if not card_token:
        logger.error(
            'Cannot activate subscription %s: no cardToken',
            payment_link.unique_id,
        )
        return

    today = timezone.now().date()
    payment_link.card_token = card_token
    payment_link.subscription_status = PaymentLink.SubscriptionStatus.ACTIVE
    payment_link.next_charge_date = _next_month_first(today)
    payment_link.save(update_fields=['card_token', 'subscription_status', 'next_charge_date'])
    logger.info('Subscription activated: payment %s', payment_link.unique_id)


def _handle_subscription_charge_webhook(
    reference: str, invoice_id: str, status: str, payload: dict
) -> HttpResponse:
    """Handles webhook callbacks for recurring SubscriptionCharge payments."""
    try:
        charge_id = int(reference.split('sub-charge-', 1)[1])
        charge = SubscriptionCharge.objects.select_related('source_payment').get(id=charge_id)
    except (IndexError, ValueError, SubscriptionCharge.DoesNotExist):
        return HttpResponseBadRequest('Unknown subscription charge reference')

    if status in ('success', 'paid'):
        now = timezone.now()
        charge.status = SubscriptionCharge.Status.SUCCESS
        charge.monobank_invoice_id = invoice_id or ''
        charge.charged_at = now
        charge.save(update_fields=['status', 'monobank_invoice_id', 'charged_at'])
        pl = charge.source_payment
        pl.last_charged_at = now
        pl.next_charge_date = _next_month_first(pl.next_charge_date or now.date())
        pl.save(update_fields=['last_charged_at', 'next_charge_date'])
        logger.info('Subscription charge %s succeeded', charge_id)
    elif status in ('failure', 'expired', 'reversed'):
        err = payload.get('errText', '') or status
        charge.status = SubscriptionCharge.Status.FAILED
        charge.error_message = err
        charge.save(update_fields=['status', 'error_message'])
        logger.warning('Subscription charge %s failed: %s', charge_id, err)

    return JsonResponse({'ok': True})


def payment_page(request: HttpRequest, unique_id):
    payment_link = get_object_or_404(PaymentLink, unique_id=unique_id)

    inactive_statuses = (
        PaymentLink.Status.PAID,
        PaymentLink.Status.DEACTIVATED,
        PaymentLink.Status.EXPIRED,
    )
    # Legacy UAH links are not served on .cz (no UAH anywhere on the page).
    if payment_link.status in inactive_statuses or payment_link.is_legacy_currency:
        return _render_inactive(request, payment_link)

    payment_link.mark_first_open()
    if payment_link.is_expired():
        if payment_link.status != PaymentLink.Status.EXPIRED:
            payment_link.status = PaymentLink.Status.EXPIRED
            payment_link.save(update_fields=['status'])
        return _render_inactive(request, payment_link)

    lang = current_lang()
    texts = get_texts(lang)
    payment_settings = get_payment_settings()
    executor = (payment_settings or PaymentSettings.get_solo()).executor_snapshot()
    consents_ok = payment_link.has_checkout_consents

    files = [
        {'url': f.file.url, 'name': f.public_name(texts)}
        for f in payment_link.attached_files.all()
    ]

    blocks = build_payment_blocks(payment_link, texts, lang) if consents_ok else []
    bank_blocks = [b for b in blocks if not b['is_paypal']]
    paypal_blocks = [b for b in blocks if b['is_paypal']]

    privacy_url = reverse('privacy')
    consent_data_html = mark_safe(escape(texts['consent_data']).replace(
        '{privacy_link}',
        format_html(
            '<a href="{}" target="_blank" rel="noopener">{}</a>',
            privacy_url, texts['consent_privacy_link'],
        ),
    ))

    path_cs = path_en = ''
    for code in ('cs', 'en'):
        with translation.override(code):
            url = reverse('payment:payment_page', kwargs={'unique_id': payment_link.unique_id})
        if code == 'cs':
            path_cs = url
        else:
            path_en = url

    contact_email = ''
    try:
        from apps.core.utils import get_site_contact_settings
        contact_email = (get_site_contact_settings().email or '').strip()
    except Exception:  # contacts table unavailable — fall back to executor email
        logger.warning('Site contact settings unavailable for payment page', exc_info=True)
    contact_email = contact_email or executor.get('email', '')

    return render(request, 'payment/payment_page.html', {
        't': texts,
        'contact_email': contact_email,
        'lang': lang,
        'payment_link': payment_link,
        'payment_settings': payment_settings,
        'purpose': payment_link.payment_purpose(),
        'executor': executor,
        'expires_at_iso': payment_link.expires_at.isoformat() if payment_link.expires_at else None,
        'amount_display': format_money(payment_link.amount, lang),
        'amount_plain': plain_amount(payment_link.amount),
        'files': files,
        'consents_ok': consents_ok,
        'consent_error': request.GET.get('consent') == 'missing',
        'consent_data_html': consent_data_html,
        'bank_blocks': bank_blocks,
        'paypal_blocks': paypal_blocks,
        'path_cs': path_cs,
        'path_en': path_en,
    })


def create_invoice(request: HttpRequest, unique_id):
    """Онлайн-оплату (Monobank acquiring) на .cz вимкнено. Маршрут лишено для старих форм."""
    texts = get_texts(current_lang())
    return HttpResponse(texts['online_unavailable'], status=410, content_type='text/plain; charset=utf-8')


def record_consent(request: HttpRequest, unique_id):
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid method')

    payment_link = get_object_or_404(PaymentLink, unique_id=unique_id)
    inactive_statuses = (
        PaymentLink.Status.PAID,
        PaymentLink.Status.DEACTIVATED,
        PaymentLink.Status.EXPIRED,
    )
    if payment_link.status in inactive_statuses or payment_link.is_expired() \
            or payment_link.is_legacy_currency:
        return _render_inactive(request, payment_link)

    if not has_checkout_consents(request):
        # Обидва чекбокси обов'язкові: повертаємо на сторінку з повідомленням.
        page = reverse('payment:payment_page', kwargs={'unique_id': payment_link.unique_id})
        return redirect(f'{page}?consent=missing#consent')
    consent_error = require_and_record_consents(request, payment_link)
    if consent_error:
        return consent_error
    return redirect(payment_link_path_for_request(payment_link))


def payment_link_path_for_request(payment_link: PaymentLink) -> str:
    """Шлях сторінки оплати поточною мовою (cs без префікса, en → /en/)."""
    return reverse('payment:payment_page', kwargs={'unique_id': payment_link.unique_id}) + '#payment-details'


@csrf_exempt
def monobank_webhook(request: HttpRequest):
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid method')

    raw_body = request.body
    x_sign = request.headers.get('X-Sign') or request.META.get('HTTP_X_SIGN')

    svc = MonobankAcquiringService()
    if not svc.verify_signature(raw_body, x_sign):
        logger.warning('Monobank webhook signature verification failed')
        return HttpResponseForbidden('Invalid signature')

    try:
        payload = json.loads(raw_body.decode('utf-8'))
    except (ValueError, UnicodeDecodeError):
        return HttpResponseBadRequest('Invalid JSON')

    invoice = payload.get('invoice') if isinstance(payload.get('invoice'), dict) else {}
    invoice_id = payload.get('invoiceId') or invoice.get('invoiceId')
    status = payload.get('status') or invoice.get('status')
    reference = payload.get('reference') or invoice.get('reference')
    amount_kop = payload.get('amount') or invoice.get('amount')

    if not reference:
        return HttpResponseBadRequest('No reference')

    # ── Subscription charge webhook ───────────────────────────────────────────
    if reference.startswith('sub-charge-'):
        return _handle_subscription_charge_webhook(reference, invoice_id or '', status or '', payload)

    # ── Regular payment link webhook ─────────────────────────────────────────
    try:
        payment_link = PaymentLink.objects.get(unique_id=reference)
    except (PaymentLink.DoesNotExist, ValueError):
        return HttpResponseBadRequest('Unknown reference')

    if invoice_id and payment_link.monobank_invoice_id and \
            payment_link.monobank_invoice_id != invoice_id:
        logger.warning(
            'Monobank webhook invoiceId mismatch: link=%s expected=%s got=%s',
            payment_link.unique_id, payment_link.monobank_invoice_id, invoice_id,
        )
        return HttpResponseBadRequest('invoiceId mismatch')

    if amount_kop is not None:
        try:
            expected_kop = int((payment_link.final_amount_uah * 100).to_integral_value())
            if int(amount_kop) != expected_kop:
                logger.warning(
                    'Monobank webhook amount mismatch: link=%s expected=%s got=%s',
                    payment_link.unique_id, expected_kop, amount_kop,
                )
        except (TypeError, ValueError, InvalidOperation):
            pass

    if status in ('success', 'paid'):
        was_unpaid = payment_link.status != PaymentLink.Status.PAID
        payment_link.mark_paid()
        if was_unpaid:
            send_payment_confirmation(payment_link)
        if payment_link.is_subscription:
            _activate_subscription(payment_link, payload)
    elif status in ('expired', 'reversed', 'failure'):
        if payment_link.status not in (PaymentLink.Status.PAID, PaymentLink.Status.DEACTIVATED):
            payment_link.status = PaymentLink.Status.EXPIRED
            payment_link.save(update_fields=['status'])

    return JsonResponse({'ok': True})


def payment_success(request: HttpRequest, unique_id):
    payment_link = get_object_or_404(PaymentLink, unique_id=unique_id)
    return render(request, 'payment/payment_success.html', _status_context(request, {'payment_link': payment_link}))


def payment_failure(request: HttpRequest, unique_id):
    payment_link = get_object_or_404(PaymentLink, unique_id=unique_id)
    return render(request, 'payment/payment_failure.html', _status_context(request, {'payment_link': payment_link}))
