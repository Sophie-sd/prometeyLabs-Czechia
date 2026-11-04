"""Замовлення демо-магазину: перегляд/зміна статусу, без видалення (аудиторський слід)."""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.admin import TabularInline as UnfoldTabularInline

from .catalog_admin import ShopScopedAdminMixin
from .order_models import ShopOrder, ShopOrderItem


class ShopOrderItemInline(UnfoldTabularInline):
    model = ShopOrderItem
    extra = 0
    fields = ('product', 'product_name', 'price', 'qty')
    readonly_fields = ('product_name', 'price', 'qty')
    can_delete = False


@admin.register(ShopOrder)
class ShopOrderAdmin(ShopScopedAdminMixin, UnfoldModelAdmin):
    list_filter_sheet = False
    list_before_template = 'admin/demoshop/_sales_banner.html'
    inlines = [ShopOrderItemInline]
    list_display = ('id', 'customer_name', 'shop', 'delivery_method', 'status', 'total', 'created_at')
    list_filter = ('status', 'delivery_method')
    search_fields = ('customer_name', 'phone', 'email', 'np_city_name')
    readonly_fields = (
        'shop', 'customer_name', 'phone', 'email',
        'delivery_method',
        'np_city_name', 'np_city_name_ru', 'np_city_name_en', 'np_city_name_cs', 'np_city_ref',
        'np_warehouse_name', 'np_warehouse_name_ru', 'np_warehouse_name_en', 'np_warehouse_name_cs',
        'np_warehouse_ref',
        'address', 'address_ru', 'address_en', 'address_cs',
        'total', 'created_at',
    )
    fieldsets = (
        (_('Клієнт'), {'fields': ('shop', 'customer_name', 'phone', 'email', 'status', 'total', 'created_at')}),
        (_('Доставка'), {
            'fields': (
                'delivery_method',
                'np_city_name', 'np_city_name_ru', 'np_city_name_en', 'np_city_name_cs', 'np_city_ref',
                'np_warehouse_name', 'np_warehouse_name_ru', 'np_warehouse_name_en', 'np_warehouse_name_cs',
                'np_warehouse_ref',
                'address', 'address_ru', 'address_en', 'address_cs',
            ),
        }),
    )
    ordering = ('-created_at',)

    def get_list_display(self, request):
        fields = list(super().get_list_display(request))
        if not request.user.is_superuser and 'shop' in fields:
            fields.remove('shop')
        return fields

    # Technical / per-language delivery columns (legacy Nova Poshta schema): kept in the
    # DB, hidden from the client's CZ demo admin so it only sees one city + pickup point.
    CLIENT_HIDDEN_FIELDS = frozenset({
        'np_city_name_ru', 'np_city_name_en', 'np_city_name_cs', 'np_city_ref',
        'np_warehouse_name_ru', 'np_warehouse_name_en', 'np_warehouse_name_cs', 'np_warehouse_ref',
        'address_ru', 'address_en', 'address_cs',
    })

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if request.user.is_superuser:
            return fieldsets
        hidden = self.CLIENT_HIDDEN_FIELDS | {'shop'}
        return tuple(
            (title, {**opts, 'fields': tuple(f for f in opts['fields'] if f not in hidden)})
            for title, opts in fieldsets
        )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# Реєстрація у DemoAdminSite
from .demo_admin_site import demo_admin_site

demo_admin_site.register(ShopOrder, ShopOrderAdmin)
