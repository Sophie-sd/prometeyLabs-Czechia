"""«Створити платіжне посилання з рахунку».

Everything the client sees on the payment page comes from the invoice:
amount + currency (locked), page language, payment methods, client name/email,
payment purpose (``Invoice.payment_purpose`` — the same function as the PDF)
and the invoice PDF itself (localized «Faktura» / «Invoice» in the documents block).
"""
from __future__ import annotations

from django.core.files.base import ContentFile
from django.db import transaction

from .invoice_pdf import LegacyInvoiceError, build_pdf_filename, generate_invoice_pdf_bytes
from .models import PaymentLink, PaymentLinkFile


class InvoiceLinkError(ValueError):
    """The invoice cannot be turned into a payment link (message is shown in admin)."""


REUSABLE_STATUSES = (PaymentLink.Status.NEW, PaymentLink.Status.PENDING, PaymentLink.Status.PAID)


def existing_link_for_invoice(invoice) -> PaymentLink | None:
    """An open (or already paid) link for this invoice — never create a duplicate."""
    return invoice.payment_links.filter(status__in=REUSABLE_STATUSES).order_by('-created_at').first()


def create_payment_link_from_invoice(invoice) -> tuple[PaymentLink, bool]:
    """Returns ``(link, created)``. Raises ``InvoiceLinkError`` with a reason."""
    if invoice.is_legacy:
        raise InvoiceLinkError('Архівний рахунок (до EUR/USD) — посилання не створюється.')
    if invoice.currency not in PaymentLink.Currency.values:
        raise InvoiceLinkError('Валюта рахунку не підтримується (лише EUR / USD).')
    if not invoice.total_amount or invoice.total_amount <= 0:
        raise InvoiceLinkError('Сума рахунку 0 — додайте послуги до рахунку.')

    existing = existing_link_for_invoice(invoice)
    if existing is not None:
        return existing, False

    methods = list(
        invoice.payment_methods.filter(is_active=True, currency=invoice.currency).order_by('position', 'name')
    )
    if not methods:
        raise InvoiceLinkError(
            'У рахунку немає активних способів оплати у валюті рахунку — посилання не створено.'
        )

    try:
        pdf_bytes = generate_invoice_pdf_bytes(invoice)  # fresh: same purpose text as the page
    except LegacyInvoiceError as exc:
        raise InvoiceLinkError(str(exc)) from exc

    with transaction.atomic():
        link = PaymentLink(
            invoice=invoice,
            client_name=invoice.client_name,
            client_email=(invoice.client_email or None),
            language=invoice.language or PaymentLink.Language.CS,
            currency=invoice.currency,
            amount=invoice.total_amount,
            description=invoice.payment_purpose(),
        )
        link.full_clean(exclude=['final_amount_uah'])
        link.save()
        link.payment_methods.set(methods)
        attachment = PaymentLinkFile(payment_link=link, file_type=PaymentLinkFile.FileType.INVOICE, name='')
        attachment.file.save(build_pdf_filename(invoice), ContentFile(pdf_bytes), save=True)
    return link, True
