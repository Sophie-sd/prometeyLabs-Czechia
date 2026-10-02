"""Фейкові замовлення демо-магазину (checkout без реальної оплати)."""
from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.i18n_content import localized_text

from .catalog_models import ShopProduct
from .models import DemoShop


class ShopOrder(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', _('Нове')
        CONFIRMED = 'confirmed', _('Підтверджено')
        DONE = 'done', _('Виконано')

    shop = models.ForeignKey(
        DemoShop, on_delete=models.CASCADE, related_name='orders', verbose_name=_('Магазин'),
    )
    class DeliveryMethod(models.TextChoices):
        NP_WAREHOUSE = 'np_warehouse', _('Výdejní místo Zásilkovna')
        ADDRESS = 'address', _('Адресна доставка')

    customer_name = models.CharField(max_length=150, verbose_name=_('Клієнт'))
    phone = models.CharField(max_length=32, blank=True, verbose_name=_('Телефон'))
    email = models.EmailField(blank=True, verbose_name=_('Email'))
    delivery_method = models.CharField(
        max_length=20,
        choices=DeliveryMethod.choices,
        default=DeliveryMethod.NP_WAREHOUSE,
        verbose_name=_('Спосіб доставки'),
    )
    np_city_name = models.CharField(max_length=255, blank=True, verbose_name=_('Město (doprava)'))
    np_city_name_ru = models.CharField(max_length=255, blank=True, verbose_name=_('Město (RU)'))
    np_city_name_en = models.CharField(max_length=255, blank=True, verbose_name=_('Město (EN)'))
    np_city_name_cs = models.CharField(max_length=255, blank=True, verbose_name=_('Město (CS)'))
    np_city_ref = models.CharField(max_length=64, blank=True, verbose_name=_('Ref města'))
    np_warehouse_name = models.CharField(max_length=512, blank=True, verbose_name=_('Výdejní místo'))
    np_warehouse_name_ru = models.CharField(max_length=512, blank=True, verbose_name=_('Výdejní místo (RU)'))
    np_warehouse_name_en = models.CharField(max_length=512, blank=True, verbose_name=_('Výdejní místo (EN)'))
    np_warehouse_name_cs = models.CharField(max_length=512, blank=True, verbose_name=_('Výdejní místo (CS)'))
    np_warehouse_ref = models.CharField(max_length=64, blank=True, verbose_name=_('Ref výdejního místa'))
    address = models.CharField(max_length=300, blank=True, verbose_name=_('Адреса доставки'))
    address_ru = models.CharField(max_length=300, blank=True, verbose_name=_('Адреса доставки (RU)'))
    address_en = models.CharField(max_length=300, blank=True, verbose_name=_('Адреса доставки (EN)'))
    address_cs = models.CharField(max_length=300, blank=True, verbose_name=_('Адреса доставки (CS)'))
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.NEW, verbose_name=_('Статус'),
    )
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Сума'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Створено'))

    class Meta:
        ordering = ('-created_at',)
        verbose_name = _('Замовлення')
        verbose_name_plural = _('Замовлення')

    def __str__(self):
        return f'#{self.pk} — {self.customer_name}'


    @property
    def localized_np_city_name(self):
        return localized_text(
            self.np_city_name, self.np_city_name_ru, self.np_city_name_en, self.np_city_name_cs,
        )

    @property
    def localized_np_warehouse_name(self):
        return localized_text(
            self.np_warehouse_name, self.np_warehouse_name_ru,
            self.np_warehouse_name_en, self.np_warehouse_name_cs,
        )

    @property
    def localized_address(self):
        return localized_text(self.address, self.address_ru, self.address_en, self.address_cs)


class ShopOrderItem(models.Model):
    order = models.ForeignKey(
        ShopOrder, on_delete=models.CASCADE, related_name='items', verbose_name=_('Замовлення'),
    )
    product = models.ForeignKey(ShopProduct, on_delete=models.SET_NULL, null=True, verbose_name=_('Товар'))
    product_name = models.CharField(max_length=200, verbose_name=_('Назва (знімок)'))
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Ціна (знімок)'))
    qty = models.PositiveIntegerField(default=1, verbose_name=_('Кількість'))

    class Meta:
        verbose_name = _('Позиція замовлення')
        verbose_name_plural = _('Позиції замовлення')

    def __str__(self):
        return f'{self.product_name} × {self.qty}'

    @property
    def line_total(self):
        return self.price * self.qty
