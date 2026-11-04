"""Каталог демо-магазину в адмінці: доступ scoped до власного shop (DemoClient).

Django permissions діють на рівні моделі, не запису — реальний захист тут
дає `ShopScopedAdminMixin.get_queryset`, а не group permissions самі по собі
(django_roles_permissions_skill).
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.admin import TabularInline as UnfoldTabularInline

from .admin_fields import mirror_cs_into_base
from .catalog_models import ShopCategory, ShopProduct, ShopProductImage, ShopReview
from .models import DemoShop


class ShopScopedAdminMixin:
    """Клієнт (DemoClient) бачить і редагує лише дані свого DemoShop."""

    shop_lookup = 'shop__pk'
    # Legacy UA/RU columns stay in the DB but never reach the Czech client's form:
    # the site ships cs + en only, so the client edits `<field>_cs` and `<field>_en`.
    client_hidden_fields = frozenset()
    # `<base field>: <cs field>` — base keeps the Czech value so slugs and the
    # `localized_text(base, ru, en, cs)` fallback stay correct.
    cs_mirror_fields = {}

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        shop = getattr(request.user, 'demo_shop', None)
        if shop is None:
            return qs.none()
        return qs.filter(**{self.shop_lookup: shop.pk})

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'shop' and not request.user.is_superuser:
            shop = getattr(request.user, 'demo_shop', None)
            kwargs['queryset'] = DemoShop.objects.filter(pk=shop.pk) if shop else DemoShop.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if request.user.is_superuser:
            return fieldsets
        hidden = self.client_hidden_fields | {'shop'}
        return tuple(
            (title, {**opts, 'fields': tuple(f for f in opts['fields'] if f not in hidden)})
            for title, opts in fieldsets
        )

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and not change and getattr(obj, 'shop_id', None) is None:
            shop = getattr(request.user, 'demo_shop', None)
            if shop:
                obj.shop = shop
        if not request.user.is_superuser:
            mirror_cs_into_base(obj, self.cs_mirror_fields)
        super().save_model(request, obj, form, change)


class OwnShopCategoryFilter(admin.SimpleListFilter):
    """Category choices of this shop only, in the active language.

    Django's plain `category` filter lists every demo shop's categories, which
    both leaked other tenants' data and printed Ukrainian names on the cs/en UI.
    """

    title = _('Категорія')
    parameter_name = 'category__id__exact'

    def lookups(self, request, model_admin):
        qs = ShopCategory.objects.all()
        if not request.user.is_superuser:
            shop = getattr(request.user, 'demo_shop', None)
            qs = qs.filter(shop=shop) if shop else qs.none()
        return [(c.pk, c.localized_name) for c in qs.order_by('order', 'name')]

    def queryset(self, request, queryset):
        value = self.value()
        return queryset.filter(category__pk=value) if value else queryset


class ShopProductImageInline(UnfoldTabularInline):
    model = ShopProductImage
    extra = 0
    fields = ('image', 'alt', 'is_main', 'order')
    ordering = ('-is_main', 'order', 'id')
    verbose_name = _('Фото')
    verbose_name_plural = _('Фото товару')


@admin.register(ShopCategory)
class ShopCategoryAdmin(ShopScopedAdminMixin, UnfoldModelAdmin):
    list_filter_sheet = False
    list_before_template = 'admin/demoshop/_sales_banner.html'
    list_display = ('localized_name_column', 'shop', 'icon', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name', 'name_ru', 'name_en', 'name_cs')
    ordering = ('shop', 'order')
    client_hidden_fields = frozenset({'name', 'name_ru'})
    cs_mirror_fields = {'name': 'name_cs'}
    fieldsets = (
        (_('Основне'), {'fields': ('shop', 'name', 'name_ru', 'name_en', 'name_cs', 'slug', 'icon')}),
        (_('Видимість'), {'fields': ('is_active', 'order')}),
    )

    @admin.display(description=_('Назва'), ordering='name')
    def localized_name_column(self, obj):
        return obj.localized_name

    def get_list_display(self, request):
        fields = list(super().get_list_display(request))
        if not request.user.is_superuser and 'shop' in fields:
            fields.remove('shop')
        return fields


@admin.register(ShopProduct)
class ShopProductAdmin(ShopScopedAdminMixin, UnfoldModelAdmin):
    list_filter_sheet = False
    list_before_template = 'admin/demoshop/_sales_banner.html'
    inlines = [ShopProductImageInline]
    list_display = ('localized_name_column', 'shop', 'category', 'price', 'old_price', 'sale_end_date', 'is_active', 'is_featured', 'order')
    list_filter = ('is_active', 'is_featured', OwnShopCategoryFilter)
    search_fields = ('name', 'short_description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('shop', 'order')
    client_hidden_fields = frozenset({
        'name', 'name_ru',
        'short_description', 'short_description_ru',
        'description', 'description_ru',
        'gift_promo_text', 'gift_promo_text_ru',
    })
    cs_mirror_fields = {
        'name': 'name_cs',
        'short_description': 'short_description_cs',
        'description': 'description_cs',
        'gift_promo_text': 'gift_promo_text_cs',
    }
    fieldsets = (
        (_('Основне'), {'fields': (
            'shop', 'category', 'name', 'name_ru', 'name_en', 'name_cs', 'slug',
            'short_description', 'short_description_ru', 'short_description_en', 'short_description_cs',
            'description', 'description_ru', 'description_en', 'description_cs',
        )}),
        (_('Ціна та акція'), {'fields': (
            'price', 'old_price', 'sale_end_date',
            'gift_promo_text', 'gift_promo_text_ru', 'gift_promo_text_en', 'gift_promo_text_cs',
        )}),
        (_('Видимість'), {'fields': ('is_active', 'is_featured', 'order')}),
    )

    @admin.display(description=_('Назва'), ordering='name')
    def localized_name_column(self, obj):
        return obj.localized_name

    def get_prepopulated_fields(self, request, obj=None):
        # `name` is hidden from the client form, so the JS slug source must be the CS field.
        if request.user.is_superuser:
            return super().get_prepopulated_fields(request, obj)
        return {'slug': ('name_cs',)}

    def get_list_display(self, request):
        fields = list(super().get_list_display(request))
        if not request.user.is_superuser and 'shop' in fields:
            fields.remove('shop')
        return fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category' and not request.user.is_superuser:
            shop = getattr(request.user, 'demo_shop', None)
            kwargs['queryset'] = ShopCategory.objects.filter(shop=shop) if shop else ShopCategory.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(ShopReview)
class ShopReviewAdmin(ShopScopedAdminMixin, UnfoldModelAdmin):
    list_filter_sheet = False
    list_before_template = 'admin/demoshop/_sales_banner.html'
    list_display = ('author_name', 'shop', 'product_column', 'rating', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating')
    search_fields = ('author_name', 'text')
    ordering = ('-created_at',)
    fieldsets = (
        (_('Основне'), {'fields': ('shop', 'product', 'author_name', 'rating', 'text', 'is_approved')}),
    )

    @admin.display(description=_('Товар'), ordering='product__name')
    def product_column(self, obj):
        return obj.product.localized_name if obj.product else '—'

    def get_list_display(self, request):
        fields = list(super().get_list_display(request))
        if not request.user.is_superuser and 'shop' in fields:
            fields.remove('shop')
        return fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'product' and not request.user.is_superuser:
            shop = getattr(request.user, 'demo_shop', None)
            kwargs['queryset'] = ShopProduct.objects.filter(shop=shop) if shop else ShopProduct.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# Реєстрація у DemoAdminSite для демо-клієнтів
from .demo_admin_site import demo_admin_site

demo_admin_site.register(ShopCategory, ShopCategoryAdmin)
demo_admin_site.register(ShopProduct, ShopProductAdmin)
demo_admin_site.register(ShopReview, ShopReviewAdmin)
