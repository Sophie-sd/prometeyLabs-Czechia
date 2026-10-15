"""Моделі комерційних пропозицій (CMS-driven proposal pages)."""
from decimal import Decimal
from pathlib import Path

from django.db import models
from django.utils.translation import gettext_lazy as _


def proposal_hero_upload_to(instance, filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in {'.jpg', '.jpeg', '.png', '.webp', '.gif'}:
        ext = '.png'
    slug = instance.slug or 'proposal'
    return f'proposals/{slug}/hero{ext}'


class Proposal(models.Model):
    """Батьківська модель комерційної пропозиції."""

    slug = models.SlugField(
        max_length=160,
        unique=True,
        verbose_name=_('Slug'),
        help_text=_('URL: /proposal/<slug>/ — робіть невгадуваним'),
    )
    client_name = models.CharField(max_length=200, verbose_name=_('Клієнт'))
    title = models.CharField(max_length=300, verbose_name=_('Заголовок'))
    title_ru = models.CharField(
        max_length=300,
        blank=True,
        verbose_name=_('Заголовок (RU)'),
    )
    title_en = models.CharField(
        max_length=300,
        blank=True,
        verbose_name=_('Заголовок (EN)'),
    )
    title_cs = models.CharField(
        max_length=300,
        blank=True,
        verbose_name=_('Заголовок (CS)'),
    )
    lead = models.TextField(blank=True, verbose_name=_('Лід / підзаголовок'))
    lead_ru = models.TextField(blank=True, verbose_name=_('Лід (RU)'))
    lead_en = models.TextField(blank=True, verbose_name=_('Лід (EN)'))
    lead_cs = models.TextField(blank=True, verbose_name=_('Лід (CS)'))
    hero_image = models.ImageField(
        upload_to=proposal_hero_upload_to,
        blank=True,
        verbose_name=_('Фото херо'),
        help_text=_('Тематичне фото цього КП. Кожне нове КП — своє зображення з адмінки.'),
    )
    recommendations_lead = models.TextField(
        blank=True,
        verbose_name=_('Лід рекомендацій'),
    )
    recommendations_lead_ru = models.TextField(
        blank=True,
        verbose_name=_('Лід рекомендацій (RU)'),
    )
    recommendations_lead_en = models.TextField(
        blank=True,
        verbose_name=_('Лід рекомендацій (EN)'),
    )
    recommendations_lead_cs = models.TextField(
        blank=True,
        verbose_name=_('Лід рекомендацій (CS)'),
    )
    issued_on = models.DateField(verbose_name=_('Дата пропозиції'))
    intro_html = models.TextField(
        blank=True,
        verbose_name=_('Про компанію / стек (HTML)'),
    )
    intro_html_ru = models.TextField(
        blank=True,
        verbose_name=_('Про компанію / стек (HTML) (RU)'),
    )
    intro_html_en = models.TextField(
        blank=True,
        verbose_name=_('Про компанію / стек (HTML) (EN)'),
    )
    intro_html_cs = models.TextField(
        blank=True,
        verbose_name=_('Про компанію / стек (HTML) (CS)'),
    )
    guarantee_html = models.TextField(
        blank=True,
        verbose_name=_('Гарантія (HTML)'),
    )
    guarantee_html_ru = models.TextField(
        blank=True,
        verbose_name=_('Гарантія (HTML) (RU)'),
    )
    guarantee_html_en = models.TextField(
        blank=True,
        verbose_name=_('Гарантія (HTML) (EN)'),
    )
    guarantee_html_cs = models.TextField(
        blank=True,
        verbose_name=_('Гарантія (HTML) (CS)'),
    )
    cta_label = models.CharField(
        max_length=120,
        default='Обговорити проєкт',
        verbose_name=_('Текст CTA'),
    )
    cta_label_ru = models.CharField(
        max_length=120,
        blank=True,
        verbose_name=_('Текст CTA (RU)'),
    )
    cta_label_en = models.CharField(
        max_length=120,
        blank=True,
        verbose_name=_('Текст CTA (EN)'),
    )
    cta_label_cs = models.CharField(
        max_length=120,
        blank=True,
        verbose_name=_('Текст CTA (CS)'),
    )
    is_published = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_('Опубліковано'),
    )

    class DemoKind(models.TextChoices):
        SHOP = 'shop', _('Інтернет-магазин')
        LANDING = 'landing', _('Лендінг')
        CORPORATE = 'corporate', _('Корпоративний сайт')

    kind = models.CharField(
        max_length=20,
        choices=DemoKind.choices,
        default=DemoKind.SHOP,
        db_index=True,
        verbose_name=_('Тип демо'),
        help_text=_('Визначає, яке демо створює дія «Створити/оновити демо»'),
    )
    corp_catalog = models.BooleanField(
        default=False,
        verbose_name=_('Каталог на корпоративному сайті'),
        help_text=_(
            'Лише для типу «Корпоративний сайт»: додає розділ каталогу без оплат/кошика '
            '— кнопка «Купити» відкриває форму заявки.',
        ),
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Створено'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Оновлено'))

    class Meta:
        ordering = ('order', '-issued_on')
        verbose_name = _('Комерційна пропозиція')
        verbose_name_plural = _('Комерційні пропозиції')

    def __str__(self):
        return f'{self.client_name} — {self.title}'

    @property
    def demo_tenant(self):
        """Активний demo-тенант цього КП, незалежно від типу (для шаблонів/адмінки)."""
        for attr in ('demo_shop', 'demo_corp', 'demo_landing'):
            tenant = getattr(self, attr, None)
            if tenant is not None:
                return tenant
        return None

    @property
    def demo_cta_label(self) -> str:
        return {
            self.DemoKind.SHOP: _('Переглянути демо магазину'),
            self.DemoKind.LANDING: _('Переглянути демо лендінгу'),
            self.DemoKind.CORPORATE: _('Переглянути демо сайту'),
        }.get(self.kind, _('Переглянути демо'))

    def get_localized_title(self) -> str:
        from .i18n_content import localized_text

        return localized_text(self.title, self.title_ru, self.title_en, self.title_cs)

    def get_localized_lead(self) -> str:
        from .i18n_content import localized_text

        return localized_text(self.lead, self.lead_ru, self.lead_en, self.lead_cs)

    def get_localized_recommendations_lead(self) -> str:
        from .i18n_content import localized_text

        return localized_text(
            self.recommendations_lead,
            self.recommendations_lead_ru,
            self.recommendations_lead_en,
            self.recommendations_lead_cs,
        )

    def get_localized_cta_label(self) -> str:
        from .i18n_content import localized_text

        from django.utils.translation import gettext

        label = localized_text(self.cta_label, self.cta_label_ru, self.cta_label_en, self.cta_label_cs)
        # Default UA label without a cs/en override → use the catalog translation.
        if label == 'Обговорити проєкт':
            return gettext('Обговорити проєкт')
        return label

    def get_localized_intro_html(self) -> str:
        from .i18n_content import localized_text

        return localized_text(self.intro_html, self.intro_html_ru, self.intro_html_en, self.intro_html_cs)

    def get_localized_guarantee_html(self) -> str:
        from .i18n_content import localized_text

        return localized_text(
            self.guarantee_html, self.guarantee_html_ru, self.guarantee_html_en, self.guarantee_html_cs,
        )

    def get_safe_intro(self) -> str:
        from .portfolio_sanitize import linkify_portfolio_html

        return linkify_portfolio_html(self.get_localized_intro_html())

    def get_safe_guarantee(self) -> str:
        from .portfolio_sanitize import linkify_portfolio_html

        return linkify_portfolio_html(self.get_localized_guarantee_html())


class ProposalModule(models.Model):
    """Ключовий модуль / функціонал платформи."""

    proposal = models.ForeignKey(
        Proposal,
        on_delete=models.CASCADE,
        related_name='modules',
        verbose_name=_('Пропозиція'),
    )
    number = models.PositiveSmallIntegerField(default=1, verbose_name=_('Номер'))
    title = models.CharField(max_length=200, verbose_name=_('Заголовок'))
    title_ru = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Заголовок (RU)'),
    )
    title_en = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Заголовок (EN)'),
    )
    title_cs = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Заголовок (CS)'),
    )
    description = models.TextField(blank=True, verbose_name=_('Опис'))
    description_ru = models.TextField(blank=True, verbose_name=_('Опис (RU)'))
    description_en = models.TextField(blank=True, verbose_name=_('Опис (EN)'))
    description_cs = models.TextField(blank=True, verbose_name=_('Опис (CS)'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))

    class Meta:
        ordering = ('order', 'number', 'id')
        verbose_name = _('Модуль')
        verbose_name_plural = _('Модулі')

    def __str__(self):
        return f'{self.number}. {self.title}'

    def get_localized_title(self) -> str:
        from .i18n_content import localized_text

        return localized_text(self.title, self.title_ru, self.title_en, self.title_cs)

    def get_localized_description(self) -> str:
        from .i18n_content import localized_text

        return localized_text(self.description, self.description_ru, self.description_en, self.description_cs)


class ProposalPackage(models.Model):
    """Тарифний пакет кошторису."""

    proposal = models.ForeignKey(
        Proposal,
        on_delete=models.CASCADE,
        related_name='packages',
        verbose_name=_('Пропозиція'),
    )
    name = models.CharField(max_length=200, verbose_name=_('Назва пакету'))
    name_ru = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Назва пакету (RU)'),
    )
    name_en = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Назва пакету (EN)'),
    )
    name_cs = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Назва пакету (CS)'),
    )
    scope = models.TextField(blank=True, verbose_name=_('Що входить'))
    scope_ru = models.TextField(blank=True, verbose_name=_('Що входить (RU)'))
    scope_en = models.TextField(blank=True, verbose_name=_('Що входить (EN)'))
    scope_cs = models.TextField(blank=True, verbose_name=_('Що входить (CS)'))
    duration = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Термін'),
    )
    duration_ru = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Термін (RU)'),
    )
    duration_en = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Термін (EN)'),
    )
    duration_cs = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Термін (CS)'),
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_('Вартість'),
    )
    currency = models.CharField(
        max_length=8,
        default='€',
        verbose_name=_('Валюта'),
    )
    is_recommended = models.BooleanField(
        default=False,
        verbose_name=_('Рекомендований'),
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))

    class Meta:
        ordering = ('order', 'id')
        verbose_name = _('Пакет')
        verbose_name_plural = _('Пакети')

    def __str__(self):
        return f'{self.name} — {self.price}{self.currency}'

    def get_localized_name(self) -> str:
        from .i18n_content import localized_text

        return localized_text(self.name, self.name_ru, self.name_en, self.name_cs)

    def get_localized_scope(self) -> str:
        from .i18n_content import localized_text

        return localized_text(self.scope, self.scope_ru, self.scope_en, self.scope_cs)

    def get_localized_duration(self) -> str:
        from .i18n_content import localized_text

        return localized_text(self.duration, self.duration_ru, self.duration_en, self.duration_cs)

    def format_price(self) -> str:
        amount = self.price
        if amount == amount.to_integral_value():
            formatted = f'{int(amount):,}'.replace(',', ' ')
        else:
            formatted = f'{amount:,.2f}'.replace(',', ' ')
        return f'{formatted} {self.currency}'.strip()


class ProposalSpec(models.Model):
    """ТЗ / індивідуальні деталі або умови оплати."""

    class Kind(models.TextChoices):
        SPEC = 'spec', _('ТЗ / деталі проєкту')
        PAYMENT = 'payment', _('Умови оплати')
        RECOMMENDATION = 'recommendation', _('Рекомендації PrometeyLabs')

    proposal = models.ForeignKey(
        Proposal,
        on_delete=models.CASCADE,
        related_name='specs',
        verbose_name=_('Пропозиція'),
    )
    kind = models.CharField(
        max_length=20,
        choices=Kind.choices,
        default=Kind.SPEC,
        db_index=True,
        verbose_name=_('Тип'),
    )
    title = models.CharField(max_length=200, verbose_name=_('Заголовок'))
    title_ru = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Заголовок (RU)'),
    )
    title_en = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Заголовок (EN)'),
    )
    title_cs = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Заголовок (CS)'),
    )
    body = models.TextField(blank=True, verbose_name=_('Текст'))
    body_ru = models.TextField(blank=True, verbose_name=_('Текст (RU)'))
    body_en = models.TextField(blank=True, verbose_name=_('Текст (EN)'))
    body_cs = models.TextField(blank=True, verbose_name=_('Текст (CS)'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))

    class Meta:
        ordering = ('kind', 'order', 'id')
        verbose_name = _('Специфікація')
        verbose_name_plural = _('Специфікації')

    def __str__(self):
        return f'[{self.get_kind_display()}] {self.title}'

    def get_localized_title(self) -> str:
        from .i18n_content import localized_text

        return localized_text(self.title, self.title_ru, self.title_en, self.title_cs)

    def get_localized_body(self) -> str:
        from .i18n_content import localized_text

        return localized_text(self.body, self.body_ru, self.body_en, self.body_cs)
