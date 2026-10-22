import uuid
import os
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class PaymentSettings(models.Model):
    title = models.CharField(max_length=255, default='Оплата послуг')
    description = models.TextField(blank=True, default='')
    default_contract_file = models.FileField(upload_to='contracts/', blank=True, null=True)

    # ── Виконавець (постачальник) для PDF та сторінки оплати .cz ────────
    executor_name = models.CharField(
        max_length=255,
        blank=True,
        default='FOP Dmytrenko Sofiia',
        verbose_name=_('Виконавець: назва (латиницею)'),
        help_text=_('Друкується в PDF і показується на сторінці оплати.'),
    )
    executor_address = models.CharField(
        max_length=500,
        blank=True,
        default='',
        verbose_name=_('Виконавець: адреса (англійською)'),
        help_text=_('Повна адреса реєстрації англійською (Myrhorod…). Порожнє — рядок не друкується.'),
    )
    executor_registration_number = models.CharField(
        max_length=64,
        blank=True,
        default='',
        verbose_name=_('Виконавець: реєстраційний номер'),
        help_text=_('Порожнє — рядок не друкується.'),
    )
    executor_email = models.EmailField(
        blank=True,
        default='info@prometeylabs.com',
        verbose_name=_('Виконавець: email'),
    )
    executor_website = models.CharField(
        max_length=255,
        blank=True,
        default='prometeylabs.cz',
        verbose_name=_('Виконавець: сайт'),
    )

    class Meta:
        verbose_name = _('Налаштування платіжної системи')
        verbose_name_plural = _('Налаштування платіжної системи')

    def save(self, *args, **kwargs):
        if not self.pk and PaymentSettings.objects.exists():
            raise ValidationError('Дозволено лише один запис PaymentSettings')
        super().save(*args, **kwargs)
        cache.delete('payment_settings')

    def delete(self, *args, **kwargs):
        result = super().delete(*args, **kwargs)
        cache.delete('payment_settings')
        return result

    def __str__(self):
        return self.title or f'Payment Settings #{self.pk}'

    @classmethod
    def get_solo(cls):
        obj = cls.objects.order_by('pk').first()
        if obj is None:
            obj = cls()  # unsaved defaults — nothing is written implicitly
        return obj

    def executor_snapshot(self) -> dict:
        return {
            'name': (self.executor_name or '').strip(),
            'address': (self.executor_address or '').strip(),
            'registration_number': (self.executor_registration_number or '').strip(),
            'email': (self.executor_email or '').strip(),
            'website': (self.executor_website or '').strip(),
        }


class RecipientProfile(models.Model):
    """LEGACY (UA): профіль отримувача платежу.

    Замінено моделлю ``PaymentMethod``. Таблицю й дані збережено (жодних
    видалень), з адмінки модель прибрано, на .cz-сторінці/PDF не показується.
    """
    name = models.CharField(max_length=255, verbose_name=_('Назва профілю'))
    recipient = models.CharField(max_length=255, verbose_name=_('Отримувач'))
    iban = models.CharField(max_length=100, verbose_name=_('IBAN'))
    ipn = models.CharField(max_length=50, verbose_name=_('ІПН/ЄДРПОУ'))
    bank = models.CharField(max_length=255, blank=True, default='', verbose_name=_('Банк'))
    mfo = models.CharField(max_length=20, blank=True, default='', verbose_name=_('МФО'))
    bank_edrpou = models.CharField(max_length=20, blank=True, default='', verbose_name=_('ЄДРПОУ Банку'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активний'))

    class Meta:
        ordering = ['name']
        verbose_name = _('Профіль отримувача (ФОП)')
        verbose_name_plural = _('Профілі отримувачів (ФОП)')

    def __str__(self):
        return self.name

    def as_requisites_rows(self) -> list:
        fields = [
            ('Отримувач',    self.recipient,   True),
            ('IBAN',         self.iban,         True),
            ('ІПН/ЄДРПОУ',  self.ipn,          True),
            ('Банк',         self.bank,         False),
            ('МФО',          self.mfo,          False),
            ('ЄДРПОУ Банку', self.bank_edrpou,  False),
        ]
        return [{'label': lbl, 'value': val, 'copyable': cp} for lbl, val, cp in fields if val]


class PaymentMethod(models.Model):
    """Спосіб оплати (реквізити) для .cz: SEPA EUR / SWIFT EUR / SWIFT USD / PayPal."""

    class MethodType(models.TextChoices):
        SEPA_EUR = 'sepa_eur', 'SEPA (EUR)'
        SWIFT_EUR = 'swift_eur', 'SWIFT (EUR)'
        SWIFT_USD = 'swift_usd', 'SWIFT (USD)'
        PAYPAL = 'paypal', 'PayPal'

    class Currency(models.TextChoices):
        EUR = 'EUR', 'EUR (€)'
        USD = 'USD', 'USD ($)'

    TYPE_CURRENCY = {
        MethodType.SEPA_EUR: Currency.EUR,
        MethodType.SWIFT_EUR: Currency.EUR,
        MethodType.SWIFT_USD: Currency.USD,
    }

    name = models.CharField(
        max_length=255,
        verbose_name=_('Назва (для адмінки)'),
        help_text=_('Напр. «Wise EUR SEPA». Клієнт бачить назву типу, а не це поле.'),
    )
    method_type = models.CharField(
        max_length=20,
        choices=MethodType.choices,
        default=MethodType.SEPA_EUR,
        verbose_name=_('Тип'),
    )
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.EUR,
        verbose_name=_('Валюта'),
    )
    beneficiary = models.CharField(max_length=255, blank=True, default='', verbose_name=_('Beneficiary (отримувач)'))
    iban = models.CharField(max_length=64, blank=True, default='', verbose_name=_('IBAN / номер рахунку'))
    swift_bic = models.CharField(max_length=20, blank=True, default='', verbose_name=_('SWIFT/BIC'))
    bank_name = models.CharField(max_length=255, blank=True, default='', verbose_name=_('Назва банку'))
    beneficiary_address = models.CharField(
        max_length=500, blank=True, default='', verbose_name=_('Адреса отримувача (beneficiary address)'),
    )
    paypal_email = models.EmailField(blank=True, default='', verbose_name=_('PayPal email'))
    paypal_url = models.URLField(
        blank=True,
        default='',
        verbose_name=_('PayPal посилання (опційно)'),
        help_text=_('Напр. https://paypal.me/… — тоді на сторінці оплати буде кнопка PayPal.'),
    )
    note_cs = models.TextField(blank=True, default='', verbose_name=_('Примітка для клієнта (CS)'))
    note_en = models.TextField(blank=True, default='', verbose_name=_('Примітка для клієнта (EN)'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активний'))
    position = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position', 'name']
        verbose_name = _('Спосіб оплати')
        verbose_name_plural = _('Способи оплати')

    def __str__(self):
        return f'{self.name} · {self.get_method_type_display()} · {self.currency}'

    @property
    def is_paypal(self) -> bool:
        return self.method_type == self.MethodType.PAYPAL

    def clean(self):
        errors = {}
        expected = self.TYPE_CURRENCY.get(self.method_type)
        if expected and self.currency != expected:
            errors['currency'] = _('Для типу «%(t)s» валюта має бути %(c)s.') % {
                't': self.get_method_type_display(), 'c': expected,
            }
        if self.is_paypal:
            if not (self.paypal_email or self.paypal_url):
                errors['paypal_email'] = _('Для PayPal вкажіть email або посилання.')
        else:
            if not self.beneficiary:
                errors['beneficiary'] = _('Обов\'язкове поле для банківського переказу.')
            if not self.iban:
                errors['iban'] = _('Обов\'язкове поле для банківського переказу.')
            if self.method_type in (self.MethodType.SWIFT_EUR, self.MethodType.SWIFT_USD) and not self.swift_bic:
                errors['swift_bic'] = _('Для SWIFT вкажіть SWIFT/BIC.')
        if errors:
            raise ValidationError(errors)

    def snapshot(self) -> dict:
        """Незмінна копія реквізитів (для PDF рахунку та сторінки оплати)."""
        return {
            'id': self.pk,
            'type': self.method_type,
            'currency': self.currency,
            'beneficiary': (self.beneficiary or '').strip(),
            'iban': (self.iban or '').strip(),
            'swift_bic': (self.swift_bic or '').strip(),
            'bank_name': (self.bank_name or '').strip(),
            'beneficiary_address': (self.beneficiary_address or '').strip(),
            'paypal_email': (self.paypal_email or '').strip(),
            'paypal_url': (self.paypal_url or '').strip(),
            'note_cs': (self.note_cs or '').strip(),
            'note_en': (self.note_en or '').strip(),
        }


def currency_mismatches(methods, currency: str) -> list:
    """Способи оплати, валюта яких не збігається з валютою рахунку/посилання."""
    return [m for m in methods if m.currency != currency]


def method_public_block(data: dict, texts: dict, lang: str) -> dict:
    """Публічний блок реквізитів зі snapshot-словника способу оплати."""
    mtype = data.get('type', '')
    is_paypal = mtype == PaymentMethod.MethodType.PAYPAL
    if is_paypal:
        fields = [('field_paypal_email', data.get('paypal_email'))]
    else:
        fields = [
            ('field_beneficiary', data.get('beneficiary')),
            ('field_iban', data.get('iban')),
            ('field_swift', data.get('swift_bic')),
            ('field_bank', data.get('bank_name')),
            ('field_beneficiary_address', data.get('beneficiary_address')),
        ]
    rows = [{'label': texts.get(k, ''), 'value': v} for k, v in fields if v]
    note = data.get('note_en') if lang == 'en' else data.get('note_cs')
    return {
        'type': mtype,
        'currency': data.get('currency', ''),
        'label': texts.get(f'method_{mtype}', mtype),
        'is_paypal': is_paypal,
        'rows': rows,
        'note': note or '',
        'paypal_url': data.get('paypal_url', '') if is_paypal else '',
    }


class PaymentText(models.Model):
    """CMS: тексти публічної сторінки оплати та PDF рахунку (CS / EN)."""

    key = models.CharField(max_length=64, unique=True, verbose_name=_('Ключ'))
    description = models.CharField(max_length=255, blank=True, default='', verbose_name=_('Де використовується'))
    text_cs = models.TextField(blank=True, default='', verbose_name=_('Текст (CS)'))
    text_en = models.TextField(blank=True, default='', verbose_name=_('Текст (EN)'))

    class Meta:
        ordering = ['key']
        verbose_name = _('Текст оплати / PDF')
        verbose_name_plural = _('Тексти оплати / PDF')

    def __str__(self):
        return self.key


class PaymentLink(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', _('Новий')
        PENDING = 'pending', _('Очікує')
        PAID = 'paid', _('Оплачено')
        EXPIRED = 'expired', _('Прострочено')
        DEACTIVATED = 'deactivated', _('Деактивовано')

    class Currency(models.TextChoices):
        # UAH прибрано з вибору (.cz працює лише з EUR/USD). Старі записи з
        # 'UAH' у БД лишаються як є і показуються як неактивні.
        EUR = 'EUR', 'EUR (€)'
        USD = 'USD', 'USD ($)'

    class Language(models.TextChoices):
        CS = 'cs', 'Čeština (CS)'
        EN = 'en', 'English (EN)'

    LEGACY_CURRENCY_UAH = 'UAH'

    class SubscriptionStatus(models.TextChoices):
        PENDING_CARD = 'pending_card', _('Очікує прив\'язки картки')
        ACTIVE = 'active', _('Активна')
        PAUSED = 'paused', _('Призупинена')
        CANCELLED = 'cancelled', _('Скасована')

    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    client_name = models.CharField(max_length=255, verbose_name=_('Ім\'я клієнта'))
    client_email = models.EmailField(blank=True, null=True, verbose_name=_('Email клієнта'))
    description = models.TextField(blank=True, default='', verbose_name=_('Опис замовлення'))
    recipient = models.ForeignKey(
        RecipientProfile,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_('Отримувач (ФОП)'),
        related_name='payment_links',
    )
    company_info = models.TextField(blank=True, default='', verbose_name=_('Реквізити (авто з профілю)'))
    payment_instructions = models.TextField(blank=True, default='', verbose_name=_('Інструкції'))
    contract_file = models.FileField(upload_to='contracts/', blank=True, null=True)
    # LEGACY: еквайринг Monobank вимкнено на .cz; колонку збережено, з адмінки приховано.
    use_acquiring = models.BooleanField(
        default=False,
        verbose_name=_('Еквайринг (legacy, вимкнено)'),
    )
    language = models.CharField(
        max_length=2,
        choices=Language.choices,
        default=Language.CS,
        verbose_name=_('Мова сторінки для клієнта'),
        help_text=_('Посилання для клієнта веде на версію сторінки цією мовою.'),
    )
    payment_methods = models.ManyToManyField(
        'payment.PaymentMethod',
        blank=True,
        related_name='payment_links',
        verbose_name=_('Способи оплати'),
        help_text=_('Один або кілька. Валюта способу має збігатися з валютою посилання.'),
    )

    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.EUR,
        verbose_name=_('Валюта'),
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('Сума'))
    exchange_rate = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=Decimal('40.00'),
        verbose_name=_('Курс до UAH'),
        help_text=_('Ігнорується при валюті UAH'),
    )
    final_amount_uah = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        editable=False,
        verbose_name=_('Сума в UAH'),
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name=_('Статус'),
    )
    duration_minutes = models.PositiveIntegerField(default=0, help_text='0 — безстроково')
    first_opened_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    monobank_invoice_id = models.CharField(max_length=128, blank=True, default='')
    monobank_invoice_url = models.URLField(blank=True, default='')
    payment_processed_at = models.DateTimeField(blank=True, null=True)

    # ── Згода на чекаут (ст. 16(a)/(c) Directive 2011/83/EU, §1837 NOZ) ───────
    withdrawal_waiver_accepted_at = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_('Відмова від 14-денного відступлення — прийнято'),
        help_text=_('Момент, коли клієнт підтвердив чекбокс про втрату права відступлення перед оплатою.'),
    )
    withdrawal_waiver_accepted_ip = models.GenericIPAddressField(
        blank=True, null=True,
        verbose_name=_('IP при підтвердженні відмови від відступлення'),
    )
    data_consent_accepted_at = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_('Згода на обробку даних для оплати — прийнято'),
    )
    data_consent_accepted_ip = models.GenericIPAddressField(
        blank=True, null=True,
        verbose_name=_('IP при підтвердженні згоди на обробку даних'),
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Створено'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Оновлено'))

    # ── Підписка ─────────────────────────────────────────────────────────────
    is_subscription = models.BooleanField(
        default=False,
        verbose_name=_('Активувати підписку'),
        help_text=_('Якщо увімкнено — перший платіж збереже картку клієнта для щомісячного списання.'),
    )
    subscription_status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        blank=True,
        default='',
        verbose_name=_('Статус підписки'),
    )
    card_token = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name=_('Токен картки'),
    )
    next_charge_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Наступне списання'),
    )
    last_charged_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Останнє списання'),
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Платіжне посилання')
        verbose_name_plural = _('Платіжні посилання')

    def __str__(self):
        return f'{self.client_name} — {self.amount} {self.currency}'

    def save(self, *args, **kwargs):
        # final_amount_uah / exchange_rate — legacy-колонки (NOT NULL), значення
        # рахуються як і раніше, але ніде на .cz не показуються.
        if self.amount is not None:
            if self.currency == self.LEGACY_CURRENCY_UAH:
                self.final_amount_uah = Decimal(self.amount).quantize(Decimal('0.01'))
            elif self.exchange_rate:
                self.final_amount_uah = (self.amount * self.exchange_rate).quantize(Decimal('0.01'))
        if self.is_subscription and not self.subscription_status:
            self.subscription_status = self.SubscriptionStatus.PENDING_CARD
        super().save(*args, **kwargs)

    @property
    def is_legacy_currency(self) -> bool:
        return self.currency not in self.Currency.values

    @property
    def has_checkout_consents(self) -> bool:
        return bool(self.withdrawal_waiver_accepted_at and self.data_consent_accepted_at)

    def client_path(self) -> str:
        from django.urls import reverse
        from django.utils import translation
        lang = self.language if self.language in self.Language.values else self.Language.CS
        with translation.override(lang):
            return reverse('payment:payment_page', kwargs={'unique_id': self.unique_id})

    def mark_first_open(self):
        if not self.first_opened_at:
            self.first_opened_at = timezone.now()
            if self.duration_minutes and self.duration_minutes > 0:
                self.expires_at = self.first_opened_at + timezone.timedelta(minutes=self.duration_minutes)
            if self.status == self.Status.NEW:
                self.status = self.Status.PENDING
            self.save(update_fields=['first_opened_at', 'expires_at', 'status'])

    def is_expired(self) -> bool:
        if self.duration_minutes and self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def deactivate(self):
        self.status = self.Status.DEACTIVATED
        self.save(update_fields=['status'])

    def mark_paid(self):
        if self.status == self.Status.PAID:
            return
        self.status = self.Status.PAID
        self.payment_processed_at = timezone.now()
        self.save(update_fields=['status', 'payment_processed_at'])

    def record_checkout_consent(self, ip_address):
        """Фіксує момент і IP підтвердження обох чекбоксів чекауту."""
        now = timezone.now()
        self.withdrawal_waiver_accepted_at = now
        self.withdrawal_waiver_accepted_ip = ip_address
        self.data_consent_accepted_at = now
        self.data_consent_accepted_ip = ip_address
        self.save(update_fields=[
            'withdrawal_waiver_accepted_at', 'withdrawal_waiver_accepted_ip',
            'data_consent_accepted_at', 'data_consent_accepted_ip',
        ])


class PaymentLinkFile(models.Model):
    class FileType(models.TextChoices):
        CONTRACT = 'contract', _('Договір')
        INVOICE = 'invoice', _('Рахунок')
        OTHER = 'other', _('Інший документ')

    payment_link = models.ForeignKey(
        PaymentLink,
        on_delete=models.CASCADE,
        related_name='attached_files',
        verbose_name=_('Платіжне посилання'),
    )
    file = models.FileField(upload_to='payment_files/', verbose_name=_('Файл'))
    file_type = models.CharField(
        max_length=20,
        choices=FileType.choices,
        default=FileType.CONTRACT,
        verbose_name=_('Тип'),
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name=_('Назва (необов\'язково)'),
        help_text=_('Якщо не заповнено — показується тип файлу'),
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['file_type', 'uploaded_at']
        verbose_name = _('Файл посилання')
        verbose_name_plural = _('Файли посилання')

    def display_name(self) -> str:
        return self.name or self.get_file_type_display()

    def public_name(self, texts: dict) -> str:
        if self.name:
            return self.name
        return texts.get(f'doc_{self.file_type}') or texts.get('doc_other', '')

    def filename(self) -> str:
        return os.path.basename(self.file.name)

    def __str__(self):
        return f'{self.display_name()} — {self.filename()}'


class SubscriptionCharge(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', _('Виконується')
        SUCCESS = 'success', _('Успішно')
        FAILED = 'failed', _('Помилка')

    source_payment = models.ForeignKey(
        PaymentLink,
        on_delete=models.CASCADE,
        related_name='subscription_charges',
        verbose_name=_('Підписка'),
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_('Статус'),
    )
    amount_uah = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name=_('Сума UAH'),
    )
    monobank_invoice_id = models.CharField(
        max_length=128,
        blank=True,
        default='',
        verbose_name=_('Invoice ID Monobank'),
    )
    error_message = models.TextField(
        blank=True,
        default='',
        verbose_name=_('Помилка'),
    )
    charged_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Дата списання'),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Списання по підписці')
        verbose_name_plural = _('Списання по підписках')

    def __str__(self):
        return f'{self.source_payment.client_name} — {self.amount_uah} UAH — {self.get_status_display()}'


from .invoice_models import Invoice, InvoiceItem, InvoiceSequence  # noqa: E402,F401

