"""Unfold admin: DemoShop (лише staff PrometeyLabs) + реєстрація доменних admin-модулів."""
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from . import catalog_admin  # noqa: F401
from . import content_admin  # noqa: F401
from . import order_admin  # noqa: F401
from .models import DemoShop


@admin.register(DemoShop)
class DemoShopAdmin(UnfoldModelAdmin):
    list_filter_sheet = False
    list_display = ('name', 'proposal_link', 'is_active', 'demo_login', 'storefront_link', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug', 'demo_login')
    readonly_fields = (
        'proposal', 'slug', 'owner_user', 'demo_login',
        'created_at', 'updated_at', 'storefront_link', 'demo_admin_link',
    )
    fieldsets = (
        (_('Магазин'), {'fields': ('name', 'slug', 'proposal', 'is_active')}),
        (_('Доступ клієнта'), {
            'fields': ('owner_user', 'demo_login', 'storefront_link', 'demo_admin_link'),
            'description': _(
                'Клієнт отримує signed token link для автологіну у demo-admin. '
                'Пароль не використовується (unusable_password).'
            ),
        }),
        (_('Кольори теми'), {
            'fields': ('color_primary', 'color_primary_hover', 'color_accent', 'color_surface', 'color_text'),
        }),
        (_('Мета'), {'classes': ('collapse',), 'fields': ('created_at', 'updated_at')}),
    )

    def has_add_permission(self, request):
        # Магазини створюються лише дією «Створити демо-магазин» у Proposal
        return False

    @admin.display(description=_('КП'))
    def proposal_link(self, obj):
        url = reverse('admin:core_proposal_change', args=[obj.proposal_id])
        return format_html('<a href="{}">{}</a>', url, obj.proposal.client_name)

    @admin.display(description=_('Вітрина'))
    def storefront_link(self, obj):
        url = reverse('demoshop:home', kwargs={'shop_slug': obj.slug})
        return format_html('<a href="{}" target="_blank" rel="noopener">{}</a>', url, url)

    @admin.display(description=_('Demo Admin'))
    def demo_admin_link(self, obj):
        if not obj.pk or not obj.is_active:
            return '—'
        # Свіжий підписаний КП-лінк (генерується на кожен рендер, не зберігається)
        url = reverse('demo_open_link', kwargs={'shop_slug': obj.slug, 'kp_token': obj.get_kp_token()})
        return format_html(
            '<a href="{}?lang=cs" target="_blank" rel="noopener noreferrer">{}</a>',
            url, _('КП-лінк у demo admin'),
        )
