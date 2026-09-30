from django import forms
from django.contrib import admin, messages
from tinymce.widgets import AdminTinyMCE
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.contrib.filters.admin import (
    ChoicesDropdownFilter,
    RangeDateFilter,
    RelatedDropdownFilter,
)
from django.utils.html import format_html
from django.utils import timezone
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.actions import delete_selected
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group, User
from .admin_filters import BooleanDropdownFilter
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from datetime import timedelta
import csv
from .models import (
    Client,
    FormSubmission,
    SiteContactSettings,
    PortfolioProject,
)
from .portfolio_sanitize import linkify_portfolio_html
from .admin_widgets import PortfolioImageWidget
from . import proposal_admin  # noqa: F401 — реєстрація ProposalAdmin

PORTFOLIO_IMAGE_WIDGETS = {
    'card_image': PortfolioImageWidget,
    'card_image_mobile': PortfolioImageWidget,
    'home_story_image': PortfolioImageWidget,
    'modal_hero': PortfolioImageWidget,
    'modal_mobile': PortfolioImageWidget,
    'modal_tablet': PortfolioImageWidget,
    'modal_laptop': PortfolioImageWidget,
}

PORTFOLIO_MCE_ATTRS = {
    'height': 320,
    'min_height': 200,
    'plugins': 'lists link autoresize code',
    'toolbar': (
        'undo redo | bold italic underline | bullist numlist link | '
        'removeformat | code'
    ),
}


# ===== ВИДАЛЕННЯ ГРУП З ADMIN =====
admin.site.unregister(Group)

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass


@admin.register(User)
class UserAdmin(DjangoUserAdmin, UnfoldModelAdmin):
    list_filter_sheet = False
    list_filter = (
        ('is_staff', BooleanDropdownFilter),
        ('is_superuser', BooleanDropdownFilter),
        ('is_active', BooleanDropdownFilter),
        ('groups', RelatedDropdownFilter),
    )



@admin.register(FormSubmission)
class FormSubmissionAdmin(UnfoldModelAdmin):
    """CRM система управління заявками з кольоровим кодуванням та статистикою"""

    list_filter_sheet = False

    # ===== ОСНОВНА КОНФІГУРАЦІЯ =====
    list_display = [
        'id_badge', 'project_display', 'name_display', 'phone_display', 
        'form_type_badge', 'status', 'priority_badge', 'created_at_display', 
        'time_elapsed', 'assigned_to_display'
    ]
    
    list_filter = [
        ('status', ChoicesDropdownFilter),
        ('form_type', ChoicesDropdownFilter),
        ('project_type', ChoicesDropdownFilter),
        ('budget', ChoicesDropdownFilter),
        ('preferred_language', ChoicesDropdownFilter),
        ('priority', ChoicesDropdownFilter),
        ('created_at', RangeDateFilter),
        ('assigned_to', RelatedDropdownFilter),
    ]
    
    search_fields = ['name', 'phone', 'email', 'details', 'manager_comment', 'project']
    readonly_fields = [
        'created_at', 'updated_at', 'ip_address', 'user_agent',
        'priority_badge', 'consent_at', 'consent_ip',
    ]
    
    list_editable = ['status']
    date_hierarchy = 'created_at'
    list_per_page = 50
    
    # ===== FIELDSETS ДЛЯ ДЕТАЛЕЙ =====
    fieldsets = (
        (_('Контактна інформація'), {
            'fields': (
                'name', 'phone', 'email', 'messenger_type', 'messenger_link',
                'preferred_language',
            )
        }),
        (_('Класифікація'), {
            'fields': (
                'project', 'project_type', 'budget', 'form_type',
                'status', 'priority', 'assigned_to',
            ),
            'classes': ('wide',)
        }),
        (_('Деталі заявки'), {
            'fields': ('details',),
            'classes': ('wide',)
        }),
        (_('Робота менеджера'), {
            'fields': ('manager_comment',),
            'classes': ('wide',)
        }),
        (_('Згода на обробку даних'), {
            'fields': ('consent_at', 'consent_ip'),
            'classes': ('collapse',),
        }),
        (_('Системна інформація'), {
            'fields': ('created_at', 'updated_at', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        })
    )
    
    # ===== ДІЇ (ACTIONS) =====
    actions = [
        delete_selected,
        'mark_as_in_progress', 
        'mark_as_thinking',
        'mark_as_no_contact',
        'mark_as_completed',
        'mark_as_rejected',
        'assign_to_me',
        'remove_assignment',
        'set_high_priority',
        'set_normal_priority',
        'set_low_priority',
        'export_as_csv'
    ]
    
    # ===== СТИЛІ =====
    class Media:
        css = {
            'all': ['admin/css/form_submissions_colors.css']
        }
    
    # ===== МЕТОДИ DISPLAY =====
    
    def id_badge(self, obj):
        """ID з малюнком"""
        return format_html(
            '<span class="admin-badge admin-badge--id">#{}</span>',
            obj.id,
        )
    id_badge.short_description = 'ID'
    
    def name_display(self, obj):
        """Ім'я з перевіркою на довгі значення"""
        return obj.name[:30] + '...' if len(obj.name) > 30 else obj.name
    name_display.short_description = _('Ім\'я')
    
    def phone_display(self, obj):
        """Телефон як посилання"""
        return format_html(
            '<a href="tel:{}" style="text-decoration: none;">{}</a>',
            obj.phone, obj.phone
        )
    phone_display.short_description = _('Телефон')
    
    def project_display(self, obj):
        """Проект — короткий опис або тире якщо порожнє"""
        if obj.project:
            return obj.project[:50] + '...' if len(obj.project) > 50 else obj.project
        return '—'
    project_display.short_description = _('Проект')
    
    def form_type_badge(self, obj):
        """Тип форми з малюнком"""
        form_type = obj.form_type or 'manual'
        display_text = obj.get_form_type_display_uk() if obj.form_type else 'Ручна'
        return format_html(
            '<span class="admin-badge admin-badge--form-type admin-badge--form-type-{}">{}</span>',
            form_type,
            display_text,
        )
    form_type_badge.short_description = _('Тип форми')
    
    def status_badge(self, obj):
        """Статус з кольором та текстом"""
        return format_html(
            '<span class="admin-badge admin-badge--status admin-badge--status-{}">{}</span>',
            obj.status,
            obj.get_status_display(),
        )
    status_badge.short_description = _('Статус')

    def priority_badge(self, obj):
        """Пріоритет з відповідним кольором"""
        return format_html(
            '<span class="admin-badge admin-badge--priority admin-badge--priority-{}">{}</span>',
            obj.priority,
            obj.get_priority_display(),
        )
    priority_badge.short_description = _('Пріоритет')
    
    def created_at_display(self, obj):
        """Дата створення в форматованому вигляді"""
        return obj.created_at.strftime('%d.%m.%Y %H:%M')
    created_at_display.short_description = _('Дата')
    
    def time_elapsed(self, obj):
        """Час з моменту створення"""
        return obj.time_since_created()
    time_elapsed.short_description = _('Минуло')
    
    def is_urgent_indicator(self, obj):
        """Індикатор критичних заявок"""
        if obj.is_urgent():
            return format_html(
                '<span style="color: white; background-color: red; '
                'padding: 4px 8px; border-radius: 4px; font-weight: bold; '
                'display: inline-block;">⚠️ КРИТИЧНО</span>'
            )
        return '—'
    is_urgent_indicator.short_description = _('Критично')
    
    def assigned_to_display(self, obj):
        """Відображення призначення"""
        if obj.assigned_to:
            return format_html(
                '<span style="background-color: #d4edda; color: #155724; '
                'padding: 4px 8px; border-radius: 4px;">{}</span>',
                obj.assigned_to.get_full_name() or obj.assigned_to.username
            )
        return format_html(
            '<span style="color: #999;">—</span>'
        )
    assigned_to_display.short_description = _('Призначено')
    
    def extra_data_formatted(self, obj):
        """Форматований вивід додаткових даних"""
        if not obj.extra_data:
            return '—'
        
        import json
        try:
            formatted = json.dumps(obj.extra_data, indent=2, ensure_ascii=False)
            return format_html('<pre style="background: #f5f5f5; padding: 10px; border-radius: 4px;">{}</pre>', formatted)
        except:
            return str(obj.extra_data)
    extra_data_formatted.short_description = _('Додаткові дані')
    
    # ===== ДІЇ =====
    
    def mark_as_in_progress(self, request, queryset):
        """Перевести в роботу"""
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'✓ {updated} заявок переведено в роботу.')
    mark_as_in_progress.short_description = "➜ Перевести в роботу"
    
    def mark_as_thinking(self, request, queryset):
        """Позначити як 'Думає'"""
        updated = queryset.update(status='thinking')
        self.message_user(request, f'✓ {updated} заявок позначено як "Думає".')
    mark_as_thinking.short_description = "⏸ Позначити як 'Думає'"
    
    def mark_as_no_contact(self, request, queryset):
        """Позначити як 'Не на зв'язку'"""
        updated = queryset.update(status='no_contact')
        self.message_user(request, f'✓ {updated} заявок позначено як "Не на зв\'язку".')
    mark_as_no_contact.short_description = "❌ Позначити як 'Не на зв'язку'"
    
    def mark_as_completed(self, request, queryset):
        """Позначити як 'Завершено'"""
        updated = queryset.update(status='completed')
        self.message_user(request, f'✓ {updated} заявок позначено як «Завершено». Розробку завершено! 🎉')
    mark_as_completed.short_description = "✅ Позначити як «Завершено»"
    
    def mark_as_rejected(self, request, queryset):
        """Позначити як 'Архів заявок'"""
        updated = queryset.update(status='rejected')
        self.message_user(request, f'✓ {updated} заявок позначено як "Архів заявок".')
    mark_as_rejected.short_description = "🗑 Позначити як 'Архів заявок'"
    
    def assign_to_me(self, request, queryset):
        """Призначити на себе"""
        updated = queryset.update(assigned_to=request.user)
        self.message_user(request, f'✓ {updated} заявок призначено на вас.')
    assign_to_me.short_description = "👤 Призначити на мене"
    
    def remove_assignment(self, request, queryset):
        """Зняти призначення"""
        updated = queryset.update(assigned_to=None)
        self.message_user(request, f'✓ Призначення знято для {updated} заявок.')
    remove_assignment.short_description = "👤❌ Зняти призначення"
    
    def set_high_priority(self, request, queryset):
        """Встановити високий пріоритет"""
        updated = queryset.update(priority='high')
        self.message_user(request, f'✓ {updated} заявок встановлено високий пріоритет.')
    set_high_priority.short_description = "🔴 Встановити ВИСОКИЙ пріоритет"
    
    def set_normal_priority(self, request, queryset):
        """Встановити нормальний пріоритет"""
        updated = queryset.update(priority='normal')
        self.message_user(request, f'✓ {updated} заявок встановлено нормальний пріоритет.')
    set_normal_priority.short_description = "🟡 Встановити нормальний пріоритет"
    
    def set_low_priority(self, request, queryset):
        """Встановити низький пріоритет"""
        updated = queryset.update(priority='low')
        self.message_user(request, f'✓ {updated} заявок встановлено низький пріоритет.')
    set_low_priority.short_description = "🟢 Встановити низький пріоритет"
    
    def export_as_csv(self, request, queryset):
        """Експорт в CSV"""
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = f'attachment; filename="submissions_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        # Додаємо BOM для правильного кодування в Excel
        response.write('\ufeff')
        
        writer = csv.writer(response)
        
        # Заголовок
        writer.writerow([
            'ID', 'Ім\'я', 'Телефон', 'Email', 'Тип форми', 'Статус', 
            'Пріоритет', 'Дата', 'Деталі', 'Коментар менеджера', 'Призначено'
        ])
        
        # Дані
        for submission in queryset:
            writer.writerow([
                submission.id,
                submission.name,
                submission.phone,
                submission.email,
                submission.get_form_type_display(),
                submission.get_status_display(),
                submission.get_priority_display(),
                submission.created_at.strftime('%d.%m.%Y %H:%M'),
                submission.details[:100] if submission.details else '',
                submission.manager_comment[:100] if submission.manager_comment else '',
                str(submission.assigned_to) if submission.assigned_to else ''
            ])
        
        self.message_user(request, f'✓ Експортовано {queryset.count()} заявок у CSV.')
        return response
    export_as_csv.short_description = "📊 Експортувати у CSV"
    
    # ===== CHANGELIST VIEW З СТАТИСТИКОЮ =====
    
    def changelist_view(self, request, extra_context=None):
        """Додаємо статистику в changelist"""
        extra_context = extra_context or {}
        
        # Загальна статистика
        total_count = FormSubmission.objects.count()
        
        # Статистика по статусах
        status_stats = FormSubmission.objects.values('status').annotate(
            count=models.Count('id')
        ).order_by('status')
        
        # Критичні заявки (>24 години в статусі 'new')
        urgent_count = FormSubmission.objects.filter(
            status='new',
            created_at__lt=timezone.now() - timedelta(hours=24)
        ).count()
        
        # Заявки без призначення
        unassigned_count = FormSubmission.objects.filter(assigned_to__isnull=True).count()
        
        # Успішні угоди (статус 'completed') за останній місяць
        one_month_ago = timezone.now() - timedelta(days=30)
        completed_this_month = FormSubmission.objects.filter(
            status='completed',
            updated_at__gte=one_month_ago
        ).count()
        
        extra_context.update({
            'total_count': total_count,
            'status_stats': status_stats,
            'urgent_count': urgent_count,
            'unassigned_count': unassigned_count,
            'completed_this_month': completed_this_month,
        })
        
        return super().changelist_view(request, extra_context)
    
    # ===== ВИДАЛЕННЯ =====
    
    def delete_queryset(self, request, queryset):
        """Гарантує коректне bulk-видалення заявок з логуванням."""
        count, deleted_by_model = queryset.delete()
        self.message_user(
            request, 
            _('Видалено %(count)d заявок.') % {'count': count}, 
            messages.SUCCESS
        )
    
    def delete_model(self, request, obj):
        """Гарантує коректне одиночне видалення заявки."""
        super().delete_model(request, obj)
        self.message_user(
            request, 
            _('Заявку видалено.'), 
            messages.SUCCESS
        )
    
    # ===== QUERYSET ОПТИМІЗАЦІЯ =====
    
    def get_queryset(self, request):
        """Оптимізація select_related для assigned_to."""
        qs = super().get_queryset(request)
        return qs.select_related('assigned_to')
    
    def get_changeform_initial_data(self, request):
        """Встановлює замовчування для нових заявок при додаванні через адмінку"""
        initial = super().get_changeform_initial_data(request)
        initial['form_type'] = 'manual'
        return initial


@admin.register(SiteContactSettings)
class SiteContactSettingsAdmin(UnfoldModelAdmin):
    """Singleton: телефон, email, соцмережі, Google Maps."""

    list_display = ('phone_display', 'email')
    list_filter_sheet = False

    fieldsets = (
        (_('Контакти'), {
            'fields': (
                'phone_display', 'phone_e164', 'email',
                'address', 'address_ru', 'address_en', 'address_cs',
                'czechia_address', 'czechia_address_en', 'czechia_address_cs',
            ),
        }),
        (_('Impressum / трейдер (футер сайту)'), {
            'fields': (
                'legal_name', 'legal_name_ru', 'legal_name_en', 'legal_name_cs',
                'registration_number',
                'legal_address', 'legal_address_ru', 'legal_address_en', 'legal_address_cs',
                'data_protection_email',
            ),
            'description': _(
                'Відображається у блоці Impressum у футері на кожній сторінці сайту '
                '(вимога прозорості трейдера для ЄС-клієнтів).'
            ),
        }),
        (_('Соціальні мережі'), {
            'fields': ('instagram_url', 'facebook_url', 'linkedin_url', 'tiktok_url'),
        }),
        (_('Месенджери'), {
            'fields': ('telegram_url', 'whatsapp_url', 'viber_url'),
        }),
        (_('Google Maps'), {
            'fields': (
                'google_maps_embed_url',
                'maps_latitude',
                'maps_longitude',
                'maps_zoom',
            ),
            'description': _(
                'Вкажіть URL вбудованої карти або координати точки. '
                'Карта з’явиться на сторінці контактів.'
            ),
        }),
    )

    def has_add_permission(self, request):
        if SiteContactSettings.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SiteContactSettings.objects.first()
        if obj:
            return HttpResponseRedirect(
                reverse('admin:core_sitecontactsettings_change', args=[obj.pk])
            )
        return super().changelist_view(request, extra_context)


class PortfolioProjectAdminForm(forms.ModelForm):
    class Meta:
        model = PortfolioProject
        fields = '__all__'
        widgets = {
            'modal_content': AdminTinyMCE(mce_attrs=PORTFOLIO_MCE_ATTRS),
            **PORTFOLIO_IMAGE_WIDGETS,
        }

    def clean_modal_content(self):
        raw = self.cleaned_data.get('modal_content', '')
        return linkify_portfolio_html(raw)

    def clean_cta_url(self):
        raw = (self.cleaned_data.get('cta_url') or '').strip()
        if not raw:
            return ''
        lowered = raw.lower()
        if lowered.startswith(('javascript:', 'data:', 'vbscript:')):
            raise forms.ValidationError(
                _('Небезпечний протокол у посиланні кнопки.'),
            )
        if raw.startswith('/') and not raw.startswith('//'):
            return raw
        if lowered.startswith(('https://', 'http://', 'mailto:', 'tel:')):
            return raw
        raise forms.ValidationError(
            _('Дозволені внутрішні шляхи (/…) або http(s)/mailto/tel.'),
        )


@admin.register(PortfolioProject)
class PortfolioProjectAdmin(UnfoldModelAdmin):
    form = PortfolioProjectAdminForm
    list_filter_sheet = False
    list_display = (
        'title',
        'order',
        'is_published',
        'show_on_portfolio',
        'show_on_homepage',
        'updated_at',
    )
    list_filter = (
        ('is_published', ChoicesDropdownFilter),
        ('show_on_portfolio', BooleanDropdownFilter),
        ('show_on_homepage', BooleanDropdownFilter),
    )
    search_fields = ('title', 'subtitle', 'card_description', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = (
        'created_at',
        'updated_at',
        'card_image_preview',
        'modal_hero_preview',
    )
    ordering = ('order', 'title')

    fieldsets = (
        (_('Основне'), {
            'fields': (
                'title', 'title_ru', 'title_en', 'title_cs',
                'subtitle', 'subtitle_ru', 'subtitle_en', 'subtitle_cs',
                'slug', 'order', 'home_order',
            ),
        }),
        (_('Живий сайт → знімок'), {
            'description': _(
                'URL реального сайту клієнта. Знімок головної (desktop/mobile) генерується локально '
                'командою `python3 manage.py capture_portfolio_screens --slug <slug>` і зберігається '
                'у поля картки нижче. Посилання ніде публічно не показується.'
            ),
            'fields': ('site_url',),
        }),
        (_('Картка (/portfolio/)'), {
            'fields': (
                'card_description',
                'card_description_ru',
                'card_description_en',
                'card_description_cs',
                'integrations',
                'integrations_ru',
                'integrations_en',
                'integrations_cs',
                'card_image',
                'card_image_preview',
                'card_image_mobile',
                'card_image_alt',
                'card_image_alt_ru',
                'card_image_alt_en',
                'card_image_alt_cs',
            ),
        }),
        (_('Кнопка картки'), {
            'fields': ('cta_label', 'cta_label_ru', 'cta_label_en', 'cta_label_cs', 'cta_url'),
        }),
        (_('Модальне вікно'), {
            'classes': ('collapse',),
            'fields': (
                'modal_content',
                'modal_content_ru',
                'modal_hero',
                'modal_hero_preview',
                'modal_mobile',
                'modal_tablet',
                'modal_laptop',
            ),
        }),
        (_('Головна сторінка'), {
            'fields': ('home_story_image', 'home_story_label', 'home_story_label_ru'),
        }),
        (_('Відображення'), {
            'fields': (
                'is_published',
                'show_on_portfolio',
                'show_on_homepage',
            ),
        }),
        (_('Службове'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description=_('Прев’ю картки'))
    def card_image_preview(self, obj):
        if not obj:
            return '—'
        src = obj.get_card_image_src()
        if not src:
            return '—'
        return format_html(
            '<img src="{}" alt="" class="pl-admin-image-preview">',
            src,
        )

    @admin.display(description=_('Прев’ю модалки'))
    def modal_hero_preview(self, obj):
        if not obj:
            return '—'
        src = obj.get_modal_hero_src()
        if not src:
            return '—'
        return format_html(
            '<img src="{}" alt="" class="pl-admin-image-preview">',
            src,
        )



@admin.register(Client)
class ClientAdmin(UnfoldModelAdmin):
    list_filter_sheet = False
    list_display = (
        'name',
        'order',
        'is_active',
        'logo_preview',
        'updated_at',
    )
    list_editable = ('order', 'is_active')
    list_filter = (('is_active', BooleanDropdownFilter),)
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at', 'logo_preview')
    ordering = ('order', 'name')

    fieldsets = (
        (_('Основне'), {
            'fields': ('name', 'logo', 'logo_preview', 'order', 'is_active'),
        }),
        (_('Службове'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description=_('Прев’ю логотипу'))
    def logo_preview(self, obj):
        if not obj:
            return '—'
        src = obj.get_logo_url()
        if not src:
            return '—'
        return format_html(
            '<img src="{}" alt="" class="pl-admin-image-preview">',
            src,
        )
