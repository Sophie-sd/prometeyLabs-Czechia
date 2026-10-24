from decimal import Decimal, InvalidOperation

from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from unfold.admin import ModelAdmin as UnfoldModelAdmin, TabularInline as UnfoldTabularInline
from unfold.contrib.filters.admin import (
    ChoicesDropdownFilter,
    RangeDateFilter,
)

from .models import (
    PaymentLink,
    PaymentLinkFile,
    PaymentMethod,
    PaymentSettings,
    PaymentText,
    currency_mismatches,
)
from .texts import DEFAULT_TEXTS, LOCKED_TEXTS
from . import invoice_admin  # noqa: F401  — реєстрація InvoiceAdmin

# LEGACY (не зареєстровано в адмінці, дані в БД збережено):
#   RecipientProfile  — замінено на PaymentMethod (без МФО / ЄДРПОУ);
#   SubscriptionCharge — розділ «Підписки» прибрано з адмінки .cz.


# ── PaymentSettings (+ Виконавець) ─────────────────────────────────────────

class PaymentSettingsForm(forms.ModelForm):
    class Meta:
        model = PaymentSettings
        fields = (
            'executor_name', 'executor_address', 'executor_registration_number',
            'executor_email', 'executor_website', 'default_contract_file',
        )
        widgets = {
            'executor_name': forms.TextInput(attrs={'placeholder': 'FOP Dmytrenko Sofiia'}),
            'executor_address': forms.TextInput(attrs={
                'placeholder': 'TO FILL: street, building, Myrhorod, Poltava region, postcode, Ukraine (in English)',
            }),
            'executor_registration_number': forms.TextInput(attrs={
                'placeholder': 'TO FILL: registration number of the FOP',
            }),
            'executor_website': forms.TextInput(attrs={'placeholder': 'prometeylabs.cz'}),
        }


@admin.register(PaymentSettings)
class PaymentSettingsAdmin(UnfoldModelAdmin):
    form = PaymentSettingsForm
    list_display = ('executor_name', 'executor_registration_number', 'executor_email')
    list_filter_sheet = False
    fieldsets = (
        (_('Виконавець (постачальник) — PDF та сторінка оплати'), {
            'fields': (
                'executor_name', 'executor_address', 'executor_registration_number',
                'executor_email', 'executor_website',
            ),
            'description': _(
                'Друкується в рахунку (PDF) і показується на сторінці оплати. '
                'Адресу та реєстраційний номер — латиницею / англійською. '
                'Порожні поля не виводяться.'
            ),
        }),
        (_('Документи'), {
            'fields': ('default_contract_file',),
        }),
    )

    def has_add_permission(self, request):
        if PaymentSettings.objects.exists():
            return False
        return super().has_add_permission(request)


# ── PaymentMethod (замість «Профіль отримувача») ───────────────────────────

class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = (
            'name', 'method_type', 'currency', 'is_active', 'position',
            'beneficiary', 'iban', 'swift_bic', 'bank_name', 'beneficiary_address',
            'paypal_email', 'paypal_url', 'note_cs', 'note_en',
        )
        widgets = {
            'note_cs': forms.Textarea(attrs={'rows': 2}),
            'note_en': forms.Textarea(attrs={'rows': 2}),
        }


@admin.register(PaymentMethod)
class PaymentMethodAdmin(UnfoldModelAdmin):
    form = PaymentMethodForm
    list_display = ('name', 'method_type', 'currency', 'beneficiary', 'iban', 'is_active', 'position')
    list_editable = ('is_active', 'position')
    list_filter = ('method_type', 'currency', 'is_active')
    search_fields = ('name', 'beneficiary', 'iban', 'paypal_email')
    list_filter_sheet = False
    fieldsets = (
        (None, {
            'fields': ('name', 'method_type', 'currency', 'is_active', 'position'),
            'description': _(
                'SEPA EUR / SWIFT EUR → EUR, SWIFT USD → USD. PayPal — EUR або USD. '
                'Спосіб можна обрати лише для рахунку / посилання тієї ж валюти.'
            ),
        }),
        (_('Банківські реквізити (SEPA / SWIFT)'), {
            'fields': ('beneficiary', 'iban', 'swift_bic', 'bank_name', 'beneficiary_address'),
        }),
        (_('PayPal'), {
            'fields': ('paypal_email', 'paypal_url'),
        }),
        (_('Примітка для клієнта'), {
            'fields': ('note_cs', 'note_en'),
            'description': _('Показується під реквізитами на сторінці оплати та в PDF мовою клієнта.'),
        }),
    )

    def has_delete_permission(self, request, obj=None):
        # Не видаляємо реквізити, які вже використано (історія рахунків) — лише «Активний» = ні.
        if obj is not None and (obj.invoices.exists() or obj.payment_links.exists()):
            return False
        return super().has_delete_permission(request, obj)


# ── PaymentText (CMS-тексти сторінки оплати та PDF) ───────────────────────

@admin.register(PaymentText)
class PaymentTextAdmin(UnfoldModelAdmin):
    list_display = ('key', 'description', 'text_cs', 'text_en')
    search_fields = ('key', 'description', 'text_cs', 'text_en')
    list_filter_sheet = False
    list_per_page = 200
    readonly_fields = ('key', 'description')
    fields = ('key', 'description', 'text_cs', 'text_en')

    def get_readonly_fields(self, request, obj=None):
        if obj is not None and obj.key in LOCKED_TEXTS:
            # Fixed wording (Faktura/Invoice, Smlouva/Contract, služba/service).
            return ('key', 'description', 'text_cs', 'text_en')
        return super().get_readonly_fields(request, obj)

    def changelist_view(self, request, extra_context=None):
        ensure_payment_texts()
        return super().changelist_view(request, extra_context)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


def ensure_payment_texts():
    """Додає відсутні ключі з дефолтними текстами (наявні не змінює)."""
    existing = set(PaymentText.objects.values_list('key', flat=True))
    missing = [
        PaymentText(key=key, description=hint, text_cs=cs, text_en=en)
        for key, (hint, cs, en) in DEFAULT_TEXTS.items() if key not in existing
    ]
    if missing:
        PaymentText.objects.bulk_create(missing, ignore_conflicts=True)


# ── PaymentLink form ───────────────────────────────────────────────────────

class PaymentLinkAdminForm(forms.ModelForm):
    description = forms.CharField(
        label=_('Опис / Призначення платежу'),
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'pl-textarea-wide'}),
        required=False,
        max_length=500,
        help_text=_(
            'Мовою клієнта (CS / EN). Використовується як призначення платежу — '
            'клієнт зможе його скопіювати.'
        ),
    )

    class Meta:
        model = PaymentLink
        fields = (
            'client_name', 'client_email', 'language', 'description',
            'currency', 'amount', 'payment_methods',
            'status', 'duration_minutes',
        )
        widgets = {
            'payment_methods': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'payment_methods' in self.fields:
            qs = PaymentMethod.objects.filter(is_active=True)
            if self.instance.pk:
                qs = PaymentMethod.objects.filter(
                    _active_or_selected_q(self.instance)
                ).distinct()
            self.fields['payment_methods'].queryset = qs.order_by('position', 'name')
            self.fields['payment_methods'].required = True
        invoice = self.instance.invoice if self.instance.invoice_id else None
        if invoice is not None:
            # Amount / currency of a link created from an invoice are locked:
            # disabled fields ignore POSTed values; clean() also rejects a tampered POST.
            for name in ('amount', 'currency'):
                if name in self.fields:
                    self.fields[name].disabled = True
                    self.fields[name].help_text = _(
                        'З рахунку №%(n)s — не редагується (дорівнює сумі рахунку).'
                    ) % {'n': invoice.number}
            if 'description' in self.fields:
                # The page / PDF purpose always comes from Invoice.payment_purpose().
                self.fields['description'].disabled = True
                self.fields['description'].help_text = _(
                    'З рахунку №%(n)s: призначення платежу береться з рахунку (так само, як у PDF).'
                ) % {'n': invoice.number}

    def clean(self):
        cleaned = super().clean()
        invoice = self.instance.invoice if self.instance.invoice_id else None
        if invoice is not None:
            raw_amount = (self.data.get(self.add_prefix('amount')) or '').strip()
            if raw_amount:
                try:
                    posted = Decimal(raw_amount.replace(',', '.'))
                except InvalidOperation:
                    posted = None
                if posted != invoice.total_amount:
                    self.add_error(None, _(
                        'Сума посилання з рахунку не змінюється: має дорівнювати сумі рахунку (%(sum)s %(cur)s).'
                    ) % {'sum': invoice.total_amount, 'cur': invoice.currency})
            raw_currency = (self.data.get(self.add_prefix('currency')) or '').strip()
            if raw_currency and raw_currency != invoice.currency:
                self.add_error(None, _('Валюта посилання з рахунку не змінюється (%(cur)s).') % {
                    'cur': invoice.currency,
                })
            cleaned['amount'] = invoice.total_amount
            cleaned['currency'] = invoice.currency
        currency = cleaned.get('currency')
        methods = cleaned.get('payment_methods')
        if currency and methods is not None:
            wrong = currency_mismatches(methods, currency)
            if wrong:
                self.add_error('payment_methods', _(
                    'Валюта способу оплати не збігається з валютою посилання (%(cur)s): %(names)s'
                ) % {'cur': currency, 'names': ', '.join(m.name for m in wrong)})
        return cleaned


def _active_or_selected_q(instance):
    from django.db.models import Q
    return Q(is_active=True) | Q(payment_links=instance)


# ── PaymentLink inline ─────────────────────────────────────────────────────

class PaymentLinkFileInline(UnfoldTabularInline):
    model = PaymentLinkFile
    extra = 1
    fields = ('file_type', 'name', 'file')
    verbose_name = _('Файл')
    verbose_name_plural = _('Файли (договори, рахунки)')


@admin.register(PaymentLink)
class PaymentLinkAdmin(UnfoldModelAdmin):
    form = PaymentLinkAdminForm
    list_filter_sheet = False
    list_display = (
        'client_name', 'amount', 'currency', 'language',
        'status', 'consent_col', 'created_at_compact',
        'client_link_cell',
    )
    list_filter = (
        ('status', ChoicesDropdownFilter),
        'language',
        'currency',
        ('created_at', RangeDateFilter),
    )
    search_fields = ('client_name', 'client_email', 'unique_id')
    readonly_fields = (
        'client_link_readonly', 'invoice_readonly',
        'first_opened_at', 'expires_at', 'payment_processed_at',
        'withdrawal_waiver_accepted_at', 'withdrawal_waiver_accepted_ip',
        'data_consent_accepted_at', 'data_consent_accepted_ip',
    )
    inlines = [PaymentLinkFileInline]
    actions = ['mark_deactivated']

    fieldsets = (
        (_('Клієнт'), {
            'fields': ('client_name', 'client_email', 'language', 'client_link_readonly'),
            'description': _('Мова визначає версію сторінки (CS / EN), на яку веде посилання.'),
        }),
        (_('Замовлення / Призначення платежу'), {
            'fields': ('description',),
        }),
        (_('Сума'), {
            'fields': ('invoice_readonly', 'currency', 'amount'),
            'description': _(
                'Клієнт бачить суму у валюті посилання (EUR або USD). Для посилання з рахунку '
                'сума й валюта беруться з рахунку і не редагуються.'
            ),
        }),
        (_('Способи оплати'), {
            'fields': ('payment_methods',),
            'description': _(
                'Оберіть один або кілька. Реквізити показуються окремими блоками '
                'після того, як клієнт відмітить обидва чекбокси згоди.'
            ),
        }),
        (_('Налаштування посилання'), {
            'fields': ('status', 'duration_minutes'),
        }),
        (_('Згода на чекаут'), {
            'fields': (
                'withdrawal_waiver_accepted_at', 'withdrawal_waiver_accepted_ip',
                'data_consent_accepted_at', 'data_consent_accepted_ip',
            ),
            'classes': ('collapse',),
        }),
        (_('Системна інформація'), {
            'fields': ('first_opened_at', 'expires_at', 'payment_processed_at'),
            'classes': ('collapse',),
        }),
    )

    class Media:
        css = {'all': ('payment/css/admin.css',)}
        js = ('payment/js/copy.js', 'payment/js/admin.js')

    @admin.display(description=_('Рахунок'))
    def invoice_readonly(self, obj):
        if not obj or not obj.invoice_id:
            return '—'
        invoice = obj.invoice
        return format_html(
            '<a href="{}">№{}</a> — {} {}',
            reverse('admin:payment_invoice_change', args=[invoice.pk]),
            invoice.number, invoice.total_amount, invoice.currency,
        )

    @admin.display(description=_('Згода'), boolean=True)
    def consent_col(self, obj):
        return obj.has_checkout_consents

    @admin.display(description=_('Створено'), ordering='created_at')
    def created_at_compact(self, obj):
        if not obj.created_at:
            return '—'
        local_dt = timezone.localtime(obj.created_at)
        return local_dt.strftime('%d.%m.%Y %H:%M')

    def get_client_facing_link(self, obj) -> str:
        base = getattr(settings, 'SITE_URL', '').rstrip('/') or 'https://prometeylabs.cz'
        return f"{base}{obj.client_path()}"

    @admin.display(description=_('Посилання для клієнта'))
    def client_link_readonly(self, obj):
        if not obj or not obj.pk:
            return '—'
        return self.client_link_cell(obj)

    @admin.display(description=_('Посилання клієнта'))
    def client_link_cell(self, obj):
        url = self.get_client_facing_link(obj)
        open_label = _('Відкрити посилання')
        copy_label = _('Скопіювати посилання клієнта')
        return format_html(
            '<div class="pl-copy-row pl-copy-row--compact pl-copy-row--icons-only">'
            '<a class="pl-icon-btn pl-icon-btn--open" href="{url}" target="_blank" '
            'rel="noopener noreferrer" aria-label="{open_aria}" title="{open_title}">↗</a>'
            '<button type="button" class="pl-icon-btn pl-copy-btn" '
            'data-copy data-copy-value="{url}" '
            'aria-label="{copy_aria}" aria-pressed="false" title="{copy_title}">'
            '<span class="pl-copy-btn-icon" data-copy-icon="default" aria-hidden="true">⧉</span>'
            '<span class="pl-copy-btn-icon" data-copy-icon="done" aria-hidden="true" hidden>✓</span>'
            '</button>'
            '</div>',
            url=url,
            open_aria=open_label,
            open_title=_('Відкрити'),
            copy_aria=copy_label,
            copy_title=_('Копіювати'),
        )

    # ── Bulk actions ─────────────────────────────────────────────────────────

    @admin.action(description=_('Деактивувати вибрані посилання'))
    def mark_deactivated(self, request, queryset):
        updated = queryset.exclude(status=PaymentLink.Status.PAID).update(
            status=PaymentLink.Status.DEACTIVATED
        )
        self.message_user(request, _('Деактивовано: %(n)s') % {'n': updated})
