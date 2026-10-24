"""Admin для модуля «Рахунки»."""
from datetime import date

from django import forms
from django.contrib import admin, messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin as UnfoldModelAdmin, TabularInline as UnfoldTabularInline

from .amount_words import format_money
from .invoice_models import Invoice, InvoiceItem
from .invoice_links import InvoiceLinkError, create_payment_link_from_invoice, existing_link_for_invoice
from .invoice_pdf import LegacyInvoiceError, get_or_create_invoice_pdf
from .models import PaymentMethod, currency_mismatches


CLIENT_HINTS_HTML = mark_safe(
    '<div class="invoice-client-hints">'
    '<p class="invoice-client-hints__title">Замовник (ЄС / міжнародний клієнт):</p>'
    '<ul class="invoice-client-hints__list">'
    '<li><strong>Назва</strong> — компанія (напр. «Example s.r.o.») або імʼя та прізвище</li>'
    '<li><strong>IČO / Company ID</strong> — реєстраційний номер компанії (якщо є)</li>'
    '<li><strong>DIČ / VAT ID</strong> — опційно, якщо клієнт платник ПДВ</li>'
    '<li><strong>Адреса, країна, email</strong> — латиницею, як у реєстрі клієнта</li>'
    '</ul>'
    '</div>'
)


def method_name(data: dict) -> str:
    """Only the payment method name (no «name · type · currency» repeat)."""
    name = (data.get('name') or '').strip()
    if not name and data.get('id'):
        method = PaymentMethod.objects.filter(pk=data['id']).first()
        name = method.name if method else ''
    if not name:
        name = dict(PaymentMethod.MethodType.choices).get(data.get('type', ''), data.get('type', ''))
    return name


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        # «Од.» is hidden: the PDF unit is always «služba» / «service» (DB column kept).
        fields = ('title', 'quantity', 'price', 'position')
        widgets = {
            'title': forms.Textarea(attrs={
                'rows': 2,
                'cols': 40,
                'class': 'vLargeTextField invoice-item-title',
            }),
        }

    def clean_quantity(self):
        qty = self.cleaned_data.get('quantity')
        if qty is None or qty <= 0:
            raise forms.ValidationError(_('Кількість має бути більшою за 0.'))
        return qty

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is None or price < 0:
            raise forms.ValidationError(_('Ціна не може бути від\'ємною.'))
        return price


class InvoiceItemInline(UnfoldTabularInline):
    model = InvoiceItem
    form = InvoiceItemForm
    extra = 1
    min_num = 1
    fields = ('position', 'title', 'quantity', 'price')
    ordering = ('position', 'id')
    verbose_name = _('Послуга')
    verbose_name_plural = _('Послуги')

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        return 1

    def has_add_permission(self, request, obj=None):
        if obj:
            return False
        return super().has_add_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if obj:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj:
            return False
        return super().has_delete_permission(request, obj)


class InvoiceAdminForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = (
            'language', 'currency', 'payment_methods',
            'client_name', 'client_tax_id', 'client_vat_id',
            'client_address', 'client_country', 'client_email',
            'invoice_date', 'valid_until', 'contract_number', 'contract_date',
            'purpose_service',
        )
        widgets = {
            'payment_methods': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ('language', 'currency'):
            if name in self.fields:
                self.fields[name].required = True
                self.fields[name].choices = [
                    c for c in self.fields[name].choices if c[0]
                ]
        if 'payment_methods' in self.fields:
            self.fields['payment_methods'].queryset = PaymentMethod.objects.filter(
                is_active=True
            ).order_by('position', 'name')
            self.fields['payment_methods'].required = True
        if 'client_name' in self.fields:
            self.fields['client_name'].help_text = _(
                'Компанія (напр. «Example s.r.o.») або імʼя та прізвище — латиницею.'
            )
        if 'client_tax_id' in self.fields:
            self.fields['client_tax_id'].help_text = _('Реєстраційний номер компанії, якщо є.')
        if 'contract_number' in self.fields:
            self.fields['contract_number'].required = False
        if 'contract_date' in self.fields:
            self.fields['contract_date'].required = False
        if 'invoice_date' in self.fields and not self.instance.pk:
            self.fields['invoice_date'].initial = date.today()
        if 'valid_until' in self.fields and not self.instance.pk:
            self.fields['valid_until'].initial = Invoice.default_due_date(date.today())
            self.fields['valid_until'].required = False

    def clean(self):
        cleaned = super().clean()
        currency = cleaned.get('currency')
        methods = cleaned.get('payment_methods')
        if currency and methods is not None:
            wrong = currency_mismatches(methods, currency)
            if wrong:
                self.add_error('payment_methods', _(
                    'Валюта способу оплати не збігається з валютою рахунку (%(cur)s): %(names)s. '
                    'Напр., для рахунку в USD не можна обрати реквізити в EUR.'
                ) % {'cur': currency, 'names': ', '.join(m.name for m in wrong)})
        invoice_date = cleaned.get('invoice_date')
        due = cleaned.get('valid_until')
        if invoice_date and not due:
            cleaned['valid_until'] = Invoice.default_due_date(invoice_date)
        elif invoice_date and due and due < invoice_date:
            self.add_error('valid_until', _('Термін оплати не може бути раніше дати рахунку.'))
        number = (cleaned.get('contract_number') or '').strip()
        if number.strip('-–—. ') == '':
            # A dash is not a contract number; a date alone is never printed.
            cleaned['contract_number'] = ''
            if cleaned.get('contract_date'):
                self.add_error('contract_date', _(
                    'Дата договору без номера не друкується — вкажіть номер договору або очистіть дату.'
                ))
        return cleaned


@admin.register(Invoice)
class InvoiceAdmin(UnfoldModelAdmin):
    form = InvoiceAdminForm
    inlines = [InvoiceItemInline]
    list_filter_sheet = False
    list_display = (
        'number', 'invoice_date', 'language_col', 'client_name',
        'total_col', 'contract_col', 'created_at_col', 'pdf_col',
    )
    list_display_links = ('number',)
    search_fields = ('number', 'client_name', 'contract_number', 'client_tax_id', 'client_vat_id')
    ordering = ('-number',)
    list_per_page = 50
    change_form_template = 'admin/payment/invoice/change_form.html'
    actions = ['create_payment_links_action']

    class Media:
        css = {'all': ('payment/css/invoice_admin.css',)}
        js = ('payment/js/invoice_admin.js',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return (
                'number', 'language', 'currency', 'invoice_date', 'valid_until',
                'methods_readonly', 'payment_purpose_readonly',
                'client_name', 'client_tax_id', 'client_vat_id', 'client_address',
                'client_country', 'client_email',
                'contract_number', 'contract_date', 'purpose_service', 'total_amount',
                'created_at', 'created_by', 'payment_links_readonly',
            )
        return ('number', 'total_amount')

    def get_fieldsets(self, request, obj=None):
        if obj:
            return (
                (_('Рахунок'), {
                    'fields': (
                        'number', 'language', 'currency', 'invoice_date', 'valid_until',
                        'total_amount',
                    ),
                }),
                (_('Способи оплати'), {
                    'fields': ('methods_readonly', 'purpose_service', 'payment_purpose_readonly'),
                }),
                (_('Замовник'), {
                    'fields': (
                        'client_name', 'client_tax_id', 'client_vat_id',
                        'client_address', 'client_country', 'client_email',
                    ),
                }),
                (_('Договір'), {
                    'fields': ('contract_number', 'contract_date'),
                }),
                (_('Платіжні посилання'), {
                    'fields': ('payment_links_readonly',),
                }),
                (_('Службове'), {
                    'fields': ('created_at', 'created_by'),
                    'classes': ('collapse',),
                }),
            )
        return (
            (_('Рахунок'), {
                'fields': ('language', 'currency', 'invoice_date', 'valid_until'),
                'description': _(
                    'Номер призначається автоматично. Термін оплати за замовчуванням — '
                    'дата рахунку + 3 дні (можна змінити). PDF генерується мовою рахунку.'
                ),
            }),
            (_('Способи оплати'), {
                'fields': ('payment_methods', 'purpose_service'),
                'description': _(
                    'Оберіть один або кілька способів у валюті рахунку — реквізити кожного '
                    'друкуються в PDF. Виконавець береться з «Платежі → Налаштування». '
                    'Призначення платежу формується автоматично: «Payment for <послуга> '
                    'by the invoice № <номер> from <дата>» (CS: «Platba za … dle faktury č. … ze dne …»).'
                ),
            }),
            (_('Замовник'), {
                'fields': (
                    'client_name', 'client_tax_id', 'client_vat_id',
                    'client_address', 'client_country', 'client_email',
                ),
                'description': CLIENT_HINTS_HTML,
            }),
            (_('Договір'), {
                'fields': ('contract_number', 'contract_date'),
                'description': _(
                    'Необовʼязково. Якщо номера договору немає — рядок «Smlouva / Contract» '
                    'у PDF не друкується (дата без номера теж).'
                ),
            }),
        )

    @admin.display(description=_('Способи оплати'))
    def methods_readonly(self, obj):
        data = obj.payment_methods_snapshot or [m.snapshot() for m in obj.payment_methods.all()]
        if not data:
            return '—'
        return format_html_join(mark_safe('<br>'), '{}', ((method_name(d),) for d in data))

    @admin.display(description=_('Платіжні посилання'))
    def payment_links_readonly(self, obj):
        links = list(obj.payment_links.order_by('-created_at')) if obj and obj.pk else []
        if not links:
            return '—'
        return format_html_join(
            mark_safe('<br>'), '<a href="{}">{} — {}</a>',
            ((reverse('admin:payment_paymentlink_change', args=[link.pk]),
              link.get_status_display(), link.created_at.strftime('%d.%m.%Y %H:%M'))
             for link in links),
        )

    @admin.display(description=_('Призначення платежу'))
    def payment_purpose_readonly(self, obj):
        if obj.is_legacy:
            return '—'
        return obj.payment_purpose()

    def has_change_permission(self, request, obj=None):
        # Дозволяємо відкриття change для перегляду / PDF, але поля readonly.
        return request.user.has_perm('payment.view_invoice') or super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or super().has_delete_permission(request, obj)

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        invoice = form.instance
        # Нормалізуємо position 1..N
        for idx, item in enumerate(invoice.items.all().order_by('position', 'id'), start=1):
            if item.position != idx:
                item.position = idx
                item.save(update_fields=['position'])
            else:
                # Перерахувати amount на випадок
                item.save()
        invoice.recalculate_total()
        if not change:
            invoice.freeze_snapshots()

    def response_add(self, request, obj, post_url_continue=None):
        if '_save_and_pdf' in request.POST:
            return HttpResponseRedirect(
                reverse('admin:payment_invoice_download_pdf', args=[obj.pk])
            )
        return super().response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        if '_save_and_pdf' in request.POST:
            return HttpResponseRedirect(
                reverse('admin:payment_invoice_download_pdf', args=[obj.pk])
            )
        return super().response_change(request, obj)

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                '<path:object_id>/pdf/',
                self.admin_site.admin_view(self.download_pdf_view),
                name='payment_invoice_download_pdf',
            ),
            path(
                '<path:object_id>/create-payment-link/',
                self.admin_site.admin_view(self.create_payment_link_view),
                name='payment_invoice_create_payment_link',
            ),
        ]
        return custom + urls

    def download_pdf_view(self, request, object_id):
        invoice = Invoice.objects.filter(pk=object_id).first()
        if not invoice:
            messages.error(request, _('Рахунок не знайдено.'))
            return HttpResponseRedirect(reverse('admin:payment_invoice_changelist'))
        try:
            data, filename = get_or_create_invoice_pdf(invoice, force=True)
        except LegacyInvoiceError:
            messages.error(request, _(
                'Архівний рахунок (до переходу на EUR/USD): збереженого PDF немає, '
                'новий не генерується.'
            ))
            return HttpResponseRedirect(
                reverse('admin:payment_invoice_change', args=[object_id])
            )
        except Exception as exc:
            messages.error(request, _('Помилка генерації PDF: %s') % exc)
            return HttpResponseRedirect(
                reverse('admin:payment_invoice_change', args=[object_id])
            )
        from urllib.parse import quote
        response = HttpResponse(data, content_type='application/pdf')
        ascii_name = filename if filename.isascii() else f'Invoice_{invoice.number}.pdf'
        response['Content-Disposition'] = (
            f"attachment; filename=\"{ascii_name}\"; "
            f"filename*=UTF-8''{quote(filename)}"
        )
        return response

    def _link_from_invoice(self, request, invoice):
        try:
            link, created = create_payment_link_from_invoice(invoice)
        except InvoiceLinkError as exc:
            messages.error(request, _('Рахунок №%(n)s: %(err)s') % {'n': invoice.number, 'err': exc})
            return None
        except Exception as exc:  # PDF / storage failure — nothing half-created (atomic)
            messages.error(request, _('Рахунок №%(n)s: помилка — %(err)s') % {'n': invoice.number, 'err': exc})
            return None
        if created:
            messages.success(request, _(
                'Рахунок №%(n)s: платіжне посилання створено (сума %(sum)s %(cur)s, PDF рахунку додано).'
            ) % {'n': invoice.number, 'sum': invoice.total_amount, 'cur': invoice.currency})
        else:
            messages.info(request, _(
                'Рахунок №%(n)s: посилання вже існує — відкрито наявне (дублікат не створено).'
            ) % {'n': invoice.number})
        return link

    def create_payment_link_view(self, request, object_id):
        change_url = reverse('admin:payment_invoice_change', args=[object_id])
        if request.method != 'POST':
            return HttpResponseRedirect(change_url)
        if not request.user.has_perm('payment.add_paymentlink'):
            messages.error(request, _('Немає права створювати платіжні посилання.'))
            return HttpResponseRedirect(change_url)
        invoice = Invoice.objects.filter(pk=object_id).first()
        if not invoice:
            messages.error(request, _('Рахунок не знайдено.'))
            return HttpResponseRedirect(reverse('admin:payment_invoice_changelist'))
        link = self._link_from_invoice(request, invoice)
        if link is None:
            return HttpResponseRedirect(change_url)
        return HttpResponseRedirect(reverse('admin:payment_paymentlink_change', args=[link.pk]))

    @admin.action(description=_('Створити платіжне посилання з рахунку'), permissions=['add_payment_link'])
    def create_payment_links_action(self, request, queryset):
        for invoice in queryset.order_by('number'):
            self._link_from_invoice(request, invoice)

    def has_add_payment_link_permission(self, request):
        return request.user.has_perm('payment.add_paymentlink')

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        if object_id:
            extra_context['create_payment_link_url'] = reverse(
                'admin:payment_invoice_create_payment_link', args=[object_id]
            )
            invoice = Invoice.objects.filter(pk=object_id).first()
            existing = existing_link_for_invoice(invoice) if invoice else None
            extra_context['existing_payment_link_url'] = (
                reverse('admin:payment_paymentlink_change', args=[existing.pk]) if existing else ''
            )
            extra_context['can_create_payment_link'] = bool(
                invoice and not invoice.is_legacy and request.user.has_perm('payment.add_paymentlink')
            )
            extra_context['show_save'] = False
            extra_context['show_save_and_continue'] = False
            extra_context['show_save_and_add_another'] = False
            extra_context['invoice_pdf_url'] = reverse(
                'admin:payment_invoice_download_pdf', args=[object_id]
            )
            extra_context['invoice_is_readonly'] = True
        else:
            extra_context['invoice_is_readonly'] = False
        return super().changeform_view(request, object_id, form_url, extra_context)

    @admin.display(description=_('Мова'), ordering='language')
    def language_col(self, obj):
        return (obj.language or '—').upper()

    @admin.display(description=_('Сума'), ordering='total_amount')
    def total_col(self, obj):
        if obj.is_legacy:
            return f'{format_money(obj.total_amount, "cs")} ({_("архів")})'
        return f'{format_money(obj.total_amount, obj.language or "cs")} {obj.currency}'

    @admin.display(description=_('Договір'))
    def contract_col(self, obj):
        number = obj.contract_number_clean
        if not number:
            return '—'
        d = obj.contract_date.strftime('%d.%m.%Y') if obj.contract_date else ''
        return f'{number} / {d}' if d else number

    @admin.display(description=_('Створено'), ordering='created_at')
    def created_at_col(self, obj):
        if not obj.created_at:
            return '—'
        from django.utils import timezone
        return timezone.localtime(obj.created_at).strftime('%d.%m.%Y %H:%M')

    @admin.display(description=_('PDF'))
    def pdf_col(self, obj):
        pdf_url = reverse('admin:payment_invoice_download_pdf', args=[obj.pk])
        return format_html(
            '<a class="invoice-pdf-dl" href="{}" title="{}" aria-label="{}">'
            '<span class="material-symbols-outlined" aria-hidden="true">download</span>'
            '</a>',
            pdf_url,
            _('Завантажити PDF'),
            _('Завантажити PDF'),
        )

    def delete_model(self, request, obj):
        obj.delete()  # soft-delete

    def delete_queryset(self, request, queryset):
        queryset.delete()  # soft-delete через SoftDeleteQuerySet
