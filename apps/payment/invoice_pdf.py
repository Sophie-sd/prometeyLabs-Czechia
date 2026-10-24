"""PDF «Faktura / Akt o poskytnutých službách» / «Invoice / Act of services rendered» (xhtml2pdf).

Language (CS/EN) and currency (EUR/USD) come from the invoice. All labels
come from ``texts.get_texts`` (editable in admin → «Тексти оплати / PDF»).
"""
from __future__ import annotations

import io
import re
import unicodedata
from pathlib import Path
from typing import Dict, Optional, Tuple

from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.utils import translation

from .amount_words import amount_in_words, format_money
from .models import method_public_block
from .texts import get_texts, normalize_lang, service_unit


class LegacyInvoiceError(RuntimeError):
    """Архівний рахунок (до переходу на EUR/USD) — новий PDF не генерується."""


def _static_path(relative: str) -> Optional[Path]:
    found = find(relative)
    if found:
        return Path(found).resolve()
    fallback = Path(settings.BASE_DIR) / 'static' / relative
    if fallback.exists():
        return fallback.resolve()
    return None


def _logo_file_uri() -> str:
    path = _static_path('images/favicon-48x48.png')
    return path.as_uri() if path else ''


def _font_paths() -> Dict[str, str]:
    regular = _static_path('fonts/NotoSans-Regular.ttf')
    bold = _static_path('fonts/NotoSans-Bold.ttf')
    return {
        'regular': str(regular) if regular else '',
        'bold': str(bold) if bold else '',
    }


def _ascii_slug(value: str, fallback: str = 'client') -> str:
    text = unicodedata.normalize('NFKD', value or '').encode('ascii', 'ignore').decode('ascii')
    tokens = re.findall(r'[A-Za-z0-9]+', text)
    skip = {'S', 'R', 'O', 'SRO', 'A', 'AS', 'LTD', 'LLC', 'GMBH', 'INC', 'FOP'}
    meaningful = [t for t in tokens if t.upper() not in skip]
    return (meaningful[0] if meaningful else fallback)[:40]


def build_pdf_filename(invoice) -> str:
    lang = normalize_lang(invoice.language)
    prefix = 'Invoice' if lang == 'en' else 'Faktura'
    date_s = invoice.invoice_date.strftime('%Y-%m-%d')
    return f'{prefix}_{invoice.number}_{_ascii_slug(invoice.client_name)}_{date_s}.pdf'


def _nbsp(value: str) -> str:
    return value.replace(' ', '\u00a0')


def invoice_context(invoice) -> dict:
    lang = normalize_lang(invoice.language)
    texts = get_texts(lang)
    currency = invoice.currency
    items = []
    for item in invoice.items.all():
        items.append({
            'position': item.position,
            'title': item.title,
            'unit': service_unit(lang),  # always «služba» / «service» (item.unit is ignored)
            'quantity': format_money(item.quantity, lang).rstrip('0').rstrip(',.') if item.quantity is not None else '',
            'price_formatted': _nbsp(format_money(item.price, lang)),
            'amount_formatted': _nbsp(format_money(item.amount, lang)),
        })

    executor = invoice.executor_snapshot or {}
    if not executor:
        from .models import PaymentSettings
        executor = PaymentSettings.get_solo().executor_snapshot()

    methods_data = invoice.payment_methods_snapshot or [m.snapshot() for m in invoice.payment_methods.all()]
    methods = [method_public_block(d, texts, lang) for d in methods_data]
    methods.sort(key=lambda m: m['is_paypal'])  # bank transfers first, PayPal last
    method_rows = [methods[i:i + 2] for i in range(0, len(methods), 2)]

    fonts = _font_paths()
    page_footer = texts['pdf_page_footer'].format(
        email=executor.get('email', ''), website=executor.get('website', ''),
    ).strip(' ·')
    return {
        'lang': lang,
        't': texts,
        'invoice': invoice,
        'items': items,
        'currency': currency,
        'logo_uri': _logo_file_uri(),
        'font_regular': fonts['regular'],
        'font_bold': fonts['bold'],
        'invoice_date': invoice.invoice_date.strftime('%d.%m.%Y'),
        'due_date': invoice.valid_until.strftime('%d.%m.%Y') if invoice.valid_until else '',
        'contract_line': invoice.contract_line(texts),
        'total_formatted': _nbsp(format_money(invoice.total_amount, lang)),
        'total_words': amount_in_words(invoice.total_amount, currency, lang),
        'executor': executor,
        'methods': methods,
        'method_rows': method_rows,
        # Same function as the payment page (PaymentLink.payment_purpose) — one source.
        'purpose': invoice.payment_purpose(texts),
        'footer_note_lines': [ln for ln in texts['pdf_footer_note'].splitlines() if ln.strip()],
        'page_footer': page_footer,
    }


def render_invoice_html(invoice) -> str:
    ctx = invoice_context(invoice)
    with translation.override(ctx['lang']):
        return render_to_string('payment/invoice_pdf.html', ctx)


def _link_callback(uri, rel):
    """Дозволяє xhtml2pdf читати локальні file:// та static paths."""
    if uri.startswith('file://'):
        return uri.replace('file://', '')
    if uri.startswith('/'):
        return uri
    static_candidate = Path(settings.BASE_DIR) / 'static' / uri
    if static_candidate.exists():
        return str(static_candidate)
    found = find(uri)
    if found:
        return found
    return uri


def generate_invoice_pdf_bytes(invoice) -> bytes:
    from xhtml2pdf import pisa

    if invoice.is_legacy:
        raise LegacyInvoiceError('Legacy invoice (before EUR/USD) — PDF is not regenerated')
    html = render_invoice_html(invoice)
    result = io.BytesIO()
    pdf = pisa.CreatePDF(
        src=io.BytesIO(html.encode('utf-8')),
        dest=result,
        encoding='utf-8',
        link_callback=_link_callback,
    )
    if pdf.err:
        raise RuntimeError(f'PDF generation failed with {pdf.err} error(s)')
    return result.getvalue()


def _stored_pdf(invoice) -> bytes:
    if not invoice.pdf_file:
        return b''
    invoice.pdf_file.open('rb')
    try:
        return invoice.pdf_file.read()
    finally:
        invoice.pdf_file.close()


def get_or_create_invoice_pdf(invoice, force: bool = False) -> Tuple[bytes, str]:
    if invoice.is_legacy:
        # Архівний рахунок: віддаємо збережений файл без змін, нічого не перезаписуємо.
        data = _stored_pdf(invoice)
        if not data:
            raise LegacyInvoiceError('Legacy invoice has no stored PDF')
        return data, Path(invoice.pdf_file.name).name

    filename = build_pdf_filename(invoice)
    if not force:
        data = _stored_pdf(invoice)
        if data:
            return data, filename

    data = generate_invoice_pdf_bytes(invoice)
    if invoice.pdf_file:
        invoice.pdf_file.delete(save=False)
    invoice.pdf_file.save(filename, ContentFile(data), save=True)
    return data, filename
