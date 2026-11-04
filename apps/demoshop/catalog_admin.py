"""Каталог демо-магазину в адмінці: доступ scoped до власного shop (DemoClient).

Django permissions діють на рівні моделі, не запису — реальний захист тут
дає `ShopScopedAdminMixin.get_queryset`, а не group permissions самі по собі
(django_roles_permissions_skill).
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.admin import TabularInline as UnfoldTabularInline

from .catalog_models import ShopCategory, ShopProduct, ShopProductImage, ShopReview
from .models import DemoShop


class ShopScopedAdminMixin:
    """Клієнт (DemoClient) бачить і редагує лише дані свого DemoShop."""

    shop_lookup = 'shop__pk'

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

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and not change and getattr(obj, 'shop_id', None) is None:
            shop = getattr(request.user, 'demo_shop', None)
            if shop:
                obj.shop = shop
        super().save_model(request, obj, form, change)


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
    list_display = ('name', 'shop', 'icon', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name', 'name_ru', 'name_en', 'name_cs')
    ordering = ('shop', 'order')
    fieldsets = (
        (_('Основне'), {'fields': ('shop', 'name', 'name_ru', 'name_en', 'name_cs', 'slug', 'icon')}),
        (_('Видимість'), {'fields': ('is_active', 'order')}),
    )

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
    list_display = ('name', 'shop', 'category', 'price', 'old_price', 'sale_end_date', 'is_active', 'is_featured', 'order')
    list_filter = ('is_active', 'is_featured', 'category')
    search_fields = ('name', 'short_description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('shop', 'order')
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

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if request.user.is_superuser:
            return fieldsets
        return tuple(
            (title, {**opts, 'fields': tuple(f for f in opts['fields'] if f != 'shop')})
            for title, opts in fieldsets
        )


@admin.register(ShopReview)
class ShopReviewAdmin(ShopScopedAdminMixin, UnfoldModelAdmin):
    list_filter_sheet = False
    list_before_template = 'admin/demoshop/_sales_banner.html'
    list_display = ('author_name', 'shop', 'product', 'rating', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating')
    search_fields = ('author_name', 'text')
    ordering = ('-created_at',)

    def get_list_display(self, request):
        fields = list(super().get_list_display(request))
        if not request.user.is_superuser and 'shop' in fields:
            fields.remove('shop')
        return fields


# Реєстрація у DemoAdminSite для демо-клієнтів
from .demo_admin_site import demo_admin_site

demo_admin_site.register(ShopCategory, ShopCategoryAdmin)
demo_admin_site.register(ShopProduct, ShopProductAdmin)
demo_admin_site.register(ShopReview, ShopReviewAdmin)
