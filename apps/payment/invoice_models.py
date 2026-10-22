"""Моделі рахунків (Invoice / Faktura — акт наданих послуг), EUR / USD, CS / EN."""
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return self.update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self):
        return models.QuerySet.delete(self)


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)


class AllObjectsManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db)


class InvoiceSequence(models.Model):
    """Глобальний лічильник номерів рахунків. Стартове last_number=84 → перший next()=85."""

    last_number = models.PositiveIntegerField(default=84)

    class Meta:
        verbose_name = _('Лічильник рахунків')
        verbose_name_plural = _('Лічильники рахунків')

    def __str__(self):
        return f'InvoiceSequence last={self.last_number}'

    @classmethod
    def next_number(cls) -> int:
        with transaction.atomic():
            seq, _ = cls.objects.select_for_update().get_or_create(
                pk=1,
                defaults={'last_number': 84},
            )
            seq.last_number += 1
            seq.save(update_fields=['last_number'])
            return seq.last_number


def invoice_pdf_upload_to(instance, filename):
    return f'invoices/{instance.number}/{filename}'


DUE_DAYS_DEFAULT = 3


class Invoice(models.Model):
    class Language(models.TextChoices):
        CS = 'cs', 'Čeština (CS)'
        EN = 'en', 'English (EN)'

    class Currency(models.TextChoices):
        EUR = 'EUR', 'EUR (€)'
        USD = 'USD', 'USD ($)'

    number = models.PositiveIntegerField(
        unique=True,
        editable=False,
        verbose_name=_('№ рахунку'),
    )
    invoice_date = models.DateField(verbose_name=_('Дата рахунку'))
    # Due date. Колонка та сама (valid_until), тепер редагується; порожнє → дата + 3 дні.
    valid_until = models.DateField(
        blank=True,
        verbose_name=_('Термін оплати (due date)'),
        help_text=_('За замовчуванням — дата рахунку + 3 дні. Можна змінити.'),
    )
    language = models.CharField(
        max_length=2,
        choices=Language.choices,
        default=Language.CS,
        blank=True,
        verbose_name=_('Мова рахунку'),
    )
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.EUR,
        blank=True,
        verbose_name=_('Валюта рахунку'),
        help_text=_('Порожнє значення — архівний рахунок, створений до переходу на EUR/USD.'),
    )
    # LEGACY: старий профіль отримувача (UA). Тепер необов'язковий, з форми прибраний.
    recipient = models.ForeignKey(
        'payment.RecipientProfile',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='invoices',
        verbose_name=_('Профіль отримувача (legacy)'),
    )
    payment_methods = models.ManyToManyField(
        'payment.PaymentMethod',
        blank=True,
        related_name='invoices',
        verbose_name=_('Способи оплати'),
        help_text=_('Один або кілька. Реквізити кожного друкуються в PDF. Валюта має збігатися з валютою рахунку.'),
    )
    client_name = models.CharField(max_length=255, verbose_name=_('Замовник: назва компанії / ім\'я'))
    # Колонка та сама, що й раніше (client_tax_id), тепер — IČO / Company ID.
    client_tax_id = models.CharField(
        max_length=20,
        blank=True,
        default='',
        verbose_name=_('IČO / Company ID'),
    )
    client_vat_id = models.CharField(
        max_length=32,
        blank=True,
        default='',
        verbose_name=_('DIČ / VAT ID (опційно)'),
    )
    client_address = models.CharField(
        max_length=500,
        blank=True,
        default='',
        verbose_name=_('Адреса замовника'),
    )
    client_country = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name=_('Країна замовника'),
    )
    client_email = models.EmailField(
        blank=True,
        default='',
        verbose_name=_('Email замовника'),
    )
    purpose_service = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name=_('Послуга для призначення платежу'),
        help_text=_('Коротко, мовою рахунку (напр. «website development»). Порожнє — береться назва першої послуги.'),
    )
    contract_number = models.CharField(max_length=100, verbose_name=_('Номер договору'))
    contract_date = models.DateField(verbose_name=_('Дата договору'))
    total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False,
        verbose_name=_('Сума'),
    )
    pdf_file = models.FileField(
        upload_to=invoice_pdf_upload_to,
        blank=True,
        null=True,
        verbose_name=_('PDF'),
    )

    # Snapshot реквізитів виконавця на момент створення
    recipient_name_snapshot = models.CharField(max_length=255, blank=True, default='')
    recipient_iban_snapshot = models.CharField(max_length=100, blank=True, default='')
    recipient_ipn_snapshot = models.CharField(max_length=50, blank=True, default='')
    recipient_bank_snapshot = models.CharField(max_length=255, blank=True, default='')
    recipient_mfo_snapshot = models.CharField(max_length=20, blank=True, default='')
    recipient_bank_edrpou_snapshot = models.CharField(max_length=20, blank=True, default='')
    # Snapshot виконавця та способів оплати (.cz) на момент створення
    executor_snapshot = models.JSONField(default=dict, blank=True)
    payment_methods_snapshot = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Створено'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Оновлено'))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_invoices',
        verbose_name=_('Створив'),
    )
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()

    class Meta:
        ordering = ['-number']
        verbose_name = _('Рахунок')
        verbose_name_plural = _('Рахунки')

    def __str__(self):
        return f'Рахунок №{self.number} — {self.client_name}'

    @staticmethod
    def default_due_date(invoice_date):
        return invoice_date + timedelta(days=DUE_DAYS_DEFAULT) if invoice_date else None

    @property
    def is_legacy(self) -> bool:
        """Архівний рахунок (UAH, до переходу на EUR/USD)."""
        return self.currency not in self.Currency.values

    @property
    def due_date(self):
        return self.valid_until

    def save(self, *args, **kwargs):
        if self.invoice_date and not self.valid_until:
            self.valid_until = self.default_due_date(self.invoice_date)
        if not self.number:
            self.number = InvoiceSequence.next_number()
        if self.recipient_id and not self.recipient_name_snapshot:
            self._fill_recipient_snapshot()
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)

    def _fill_recipient_snapshot(self):
        r = self.recipient
        self.recipient_name_snapshot = (r.recipient or r.name or '').strip()
        self.recipient_iban_snapshot = (r.iban or '').strip()
        self.recipient_ipn_snapshot = (r.ipn or '').strip()
        self.recipient_bank_snapshot = (r.bank or '').strip()
        self.recipient_mfo_snapshot = (r.mfo or '').strip()
        self.recipient_bank_edrpou_snapshot = (r.bank_edrpou or '').strip()

    def freeze_snapshots(self, force: bool = False):
        """Фіксує реквізити виконавця та способів оплати для PDF."""
        from .models import PaymentSettings
        fields = []
        if force or not self.executor_snapshot:
            self.executor_snapshot = PaymentSettings.get_solo().executor_snapshot()
            fields.append('executor_snapshot')
        if force or not self.payment_methods_snapshot:
            self.payment_methods_snapshot = [m.snapshot() for m in self.payment_methods.all()]
            fields.append('payment_methods_snapshot')
        if fields and self.pk:
            self.save(update_fields=fields + ['updated_at'])

    def service_for_purpose(self) -> str:
        if (self.purpose_service or '').strip():
            return self.purpose_service.strip()
        first = self.items.order_by('position', 'id').first() if self.pk else None
        return (first.title.strip().splitlines()[0] if first and first.title else '')

    def payment_purpose(self, texts: dict | None = None) -> str:
        from .texts import get_texts
        lang = self.language or self.Language.CS
        texts = texts or get_texts(lang)
        date_s = self.invoice_date.strftime('%d.%m.%Y') if self.invoice_date else ''
        return texts['purpose_template'].format(
            service=self.service_for_purpose(), number=self.number, date=date_s,
        )

    def recalculate_total(self):
        total = Decimal('0.00')
        for item in self.items.all():
            total += item.amount
        self.total_amount = total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.save(update_fields=['total_amount', 'updated_at'])

    def contract_line(self, texts: dict | None = None) -> str:
        from .texts import get_texts
        texts = texts or get_texts(self.language or self.Language.CS)
        d = self.contract_date.strftime('%d.%m.%Y') if self.contract_date else ''
        return texts['pdf_contract_line'].format(number=self.contract_number, date=d)


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Рахунок'),
    )
    position = models.PositiveIntegerField(default=1, verbose_name=_('№'))
    title = models.TextField(verbose_name=_('Опис послуги'))
    unit = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name=_('Од.'),
        help_text=_('Порожнє — у PDF «služba» / «service».'),
    )
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('1'),
        verbose_name=_('К-сть'),
    )
    price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('Ціна'),
    )
    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False,
        verbose_name=_('Сума'),
    )

    class Meta:
        ordering = ['position', 'id']
        verbose_name = _('Послуга')
        verbose_name_plural = _('Послуги')

    def __str__(self):
        return f'{self.position}. {self.title[:60]}'

    def save(self, *args, **kwargs):
        qty = self.quantity or Decimal('0')
        price = self.price or Decimal('0')
        self.amount = (qty * price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        super().save(*args, **kwargs)
