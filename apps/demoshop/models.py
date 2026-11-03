"""Тенант демо-магазину, що генерується з комерційної пропозиції (КП)."""
import secrets
import unicodedata

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.validators import RegexValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.core.proposal_models import Proposal

HEX_COLOR_VALIDATOR = RegexValidator(
    regex=r'^#[0-9A-Fa-f]{6}$',
    message=_('Формат кольору: #RRGGBB'),
)

# Мають збігатися з дефолтами static/demoshop/css/demoshop_tokens.css.
# ShopThemeForm підставляє їх як initial для <input type=color> — інакше
# порожнє поле відкриється як #000000 і збереження форми «зафарбує» тему в чорний.
DEFAULT_THEME_COLORS = {
    'color_primary': '#D6CEC7',
    'color_primary_hover': '#C5BDB5',
    'color_accent': '#BD6843',
    'color_surface': '#F9F3ED',
    'color_text': '#221C1A',
}


def theme_css_cache_key(shop_id: int) -> str:
    return f'demoshop_theme_css_v1:{shop_id}'


class DemoShop(models.Model):
    """Один згенерований демо-магазин під конкретну комерційну пропозицію.

    Мультитенантність — на рівні даних (усе scoped через FK `shop`), не окремі
    кодові бази: одна статика (CSS/JS) на всі магазини, per-shop лише БД-записи
    і файли в media (тексти/фото/кольори).
    """

    proposal = models.OneToOneField(
        Proposal,
        on_delete=models.CASCADE,
        related_name='demo_shop',
        verbose_name=_('Комерційна пропозиція'),
    )
    owner_user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='demo_shop',
        verbose_name=_('Клієнтський логін'),
    )
    slug = models.SlugField(
        max_length=160,
        unique=True,
        allow_unicode=True,
        verbose_name=_('Slug'),
        help_text=_('URL: /demo/<slug>/ — генерується автоматично, невгадуваний'),
    )
    name = models.CharField(max_length=200, verbose_name=_('Назва магазину'))
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_('Активний'),
        help_text=_('Вимкнено — вітрина й адмінка клієнта повертають 404'),
    )
    demo_login = models.CharField(max_length=150, blank=True, verbose_name=_('Логін (демо)'))
    demo_password = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_('Пароль (демо)'),
        help_text=_('Показується лише в цій адмінці — для передачі клієнту'),
    )
    color_primary = models.CharField(
        max_length=7, blank=True, validators=[HEX_COLOR_VALIDATOR],
        verbose_name=_('Основний колір'), help_text=_('Hex, напр. #D6CEC7. Порожньо = дефолт'),
    )
    color_primary_hover = models.CharField(
        max_length=7, blank=True, validators=[HEX_COLOR_VALIDATOR],
        verbose_name=_('Основний колір (hover)'),
    )
    color_accent = models.CharField(
        max_length=7, blank=True, validators=[HEX_COLOR_VALIDATOR],
        verbose_name=_('Акцентний колір'),
    )
    color_surface = models.CharField(
        max_length=7, blank=True, validators=[HEX_COLOR_VALIDATOR],
        verbose_name=_('Фон секцій'),
    )
    color_text = models.CharField(
        max_length=7, blank=True, validators=[HEX_COLOR_VALIDATOR],
        verbose_name=_('Колір тексту'),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Створено'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Оновлено'))

    TOKEN_MAP = {
        'color_primary': '--ds-primary',
        'color_primary_hover': '--ds-primary-hover',
        'color_accent': '--ds-accent',
        'color_surface': '--ds-surface',
        'color_text': '--ds-text',
    }

    class Meta:
        ordering = ('-created_at',)
        verbose_name = _('Демо-магазин')
        verbose_name_plural = _('Демо-магазини')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Клієнт міняє колір у «Мій магазин» → theme.css має віддати нове значення
        # відразу, тому кеш інвалідується на кожен save(), а не за TTL.
        cache.delete(theme_css_cache_key(self.pk))

    def get_absolute_url(self) -> str:
        from django.urls import reverse

        return reverse('demoshop:home', kwargs={'shop_slug': self.slug})

    @staticmethod
    def generate_slug(base: str) -> str:
        # Strip diacritics: NFKD decompose + keep ASCII only
        normalized = unicodedata.normalize('NFKD', base)
        ascii_base = normalized.encode('ascii', 'ignore').decode('ascii')
        stem = slugify(ascii_base, allow_unicode=False)[:120] or 'shop'
        return f'{stem}-{secrets.token_hex(3)}'

    @staticmethod
    def generate_password() -> str:
        return secrets.token_urlsafe(9)


from .content_models import ShopBlock, ShopHeroSlide  # noqa: E402,F401
from .catalog_models import (  # noqa: E402,F401
    ShopCategory,
    ShopProduct,
    ShopProductImage,
    ShopReview,
)
from .order_models import ShopOrder, ShopOrderItem  # noqa: E402,F401
