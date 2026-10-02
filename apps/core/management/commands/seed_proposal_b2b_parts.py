"""
Management command: seed_proposal_b2b_parts

Idempotent заливка КП для B2B/B2C платформи автозапчастин (контент з PDF 20.08.2026).
"""
from datetime import date
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.i18n_content import translate_ua_to_ru
from apps.core.proposal_models import (
    Proposal,
    ProposalModule,
    ProposalPackage,
    ProposalSpec,
)
from apps.core.proposal_visual_models import ProposalArchNode, ProposalHighlight

SLUG = 'b2b-parts-platform-a7f3'

RECS_LEAD = (
    'Архітектурні та імплементаційні рішення по ТЗ платформи автозапчастин '
    '— з позиції команди з 10+ років у e-commerce.'
)

HIGHLIGHTS = [
    {'order': 0, 'title': 'Кастомний Django-стек'},
    {'order': 1, 'title': 'B2B / B2C під ключ'},
    {'order': 2, 'title': 'Пожиттєва гарантія коду'},
]

ARCH_NODES = [
    {'order': 0, 'title': 'Admin', 'caption': '', 'is_accent': False},
    {
        'order': 1,
        'title': 'B2B Cabinet 1',
        'caption': 'Prom / Rozetka',
        'is_accent': False,
    },
    {
        'order': 2,
        'title': 'B2C Storefront',
        'caption': 'PostgreSQL',
        'is_accent': True,
    },
    {
        'order': 3,
        'title': 'B2B Cabinet 2',
        'caption': 'Redis Cache',
        'is_accent': False,
    },
]

MODULES = [
    {
        'number': 1,
        'order': 0,
        'title': 'Гібридна архітектура: 2 B2B Кабінети + B2C Вітрина',
        'description': (
            'Перемикач B2C роздробу та 2 спеціалізованих B2B-кабінети '
            'для гуртовиків/СТО з обовʼязковою верифікацією та допуском від Супер-адміна.'
        ),
    },
    {
        'number': 2,
        'order': 1,
        'title': 'Кредитні ліміти та фінансовий контроль',
        'description': (
            'Індивідуальний розрахунок кредитного ліміту на кожного B2B-клієнта, '
            'автоматична генерація Актів звірок та Актів видачі/накладних у PDF.'
        ),
    },
    {
        'number': 3,
        'order': 2,
        'title': 'Багаторівнева система ролей співробітників',
        'description': (
            'Гнучкий розподіл прав доступу як усередині компанії '
            '(менеджери, бухгалтери, адміни), так і всередині кабінетів B2B-партнерів.'
        ),
    },
    {
        'number': 4,
        'order': 3,
        'title': 'Хаб маркетплейсів для дропшиперів/партнерів',
        'description': (
            'Повна свобода для партнерів: самостійне підключення кабінетів Prom.ua та Rozetka, '
            'автовивантаження XML/YML фідів та наскрізна історія замовлень.'
        ),
    },
    {
        'number': 5,
        'order': 4,
        'title': 'Крос-сумісність автозапчастин (1 до N)',
        'description': (
            'Один товар (сайлентблок/деталь) привʼязується до десятків моделей авто '
            'без дублювання карток у БД. Швидкий підбір за авто, крос-кодами та аналогами.'
        ),
    },
    {
        'number': 6,
        'order': 5,
        'title': 'Преміум Адмін-панель із глибокою навігацією',
        'description': (
            'Повна заміна стандартних адмінок: каскадне провалювання в підкатегорії, '
            'миттєві живі фільтри товарів, масове редагування та внутрішня аналітика продажів.'
        ),
    },
    {
        'number': 7,
        'order': 6,
        'title': 'Ідеальна мобільна версія (Mobile First)',
        'description': (
            'Швидкий, ергономічний інтерфейс для комфортної роботи гуртовиків '
            'та роздрібних клієнтів зі смартфонів прямо на складі чи СТО.'
        ),
    },
    {
        'number': 8,
        'order': 7,
        'title': 'Онлайн-оплата карткою та логістика',
        'description': (
            'Онлайн-оплата карткою (Visa/Mastercard, Apple Pay, Google Pay) '
            'через європейський еквайринг + B2B безготівковий розрахунок за рахунком-фактурою.'
        ),
    },
]

PACKAGES = [
    {
        'order': 0,
        'name': 'B2B / B2C Enterprise (Без ШІ)',
        'scope': (
            'Повний функціонал за ТЗ: 2 B2B кабінети + B2C вітрина, кредитна система, '
            'акти звірок/видачі, права ролей, експорт Prom/Rozetka, кастомна адмінка '
            'з крос-звʼязками, еквайринг (картка / Apple Pay / Google Pay), аналітика, деплой на сервер.'
        ),
        'duration': '3 місяці',
        'price': Decimal('11000.00'),
        'currency': '€',
        'is_recommended': False,
    },
    {
        'order': 1,
        'name': 'B2B Enterprise + AI Suite (З ШІ) PRO',
        'scope': (
            'Увесь функціонал пакету Enterprise + ШІ для користувача '
            '(розумний асистент підбору запчастин, 1500 €) + ШІ для адмін-панелі '
            '(автоматизація крос-привʼязок деталей, аналіз залишків та прогноз попиту, 1500 €).'
        ),
        'duration': '3 місяці',
        'price': Decimal('14000.00'),
        'currency': '€',
        'is_recommended': True,
    },
]

SPECS = [
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 0,
        'title': 'Специфікація каталогу',
        'body': (
            'Унікальна база запчастин зі складною крос-таблицею відповідностей '
            '(один артикул підходить під множину модифікацій авто). '
            'Провалювання по категоріях дерева в адмінці.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 1,
        'title': 'B2B Екосистема',
        'body': (
            'Модерація доступу супер-адміністратором, відображення індивідуальних оптових '
            'колонок цін, формування замовлень списком (bulk order), баланс взаєморозрахунків, '
            'акти звірки та акти прийому-передачі.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 2,
        'title': 'Маркетплейс-міст',
        'body': (
            'B2B-клієнти мають окремий кабінет для налаштування власних вивантажень '
            'на маркетплейси (Prom, Rozetka) та обробки замовлень.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.SPEC,
        'order': 3,
        'title': 'Штучний інтелект (опціонально в AI-пакеті)',
        'body': (
            'AI-помічник для клієнта (підбір сумісних запчастин за описом чи фото) + '
            'AI-асистент адмінки (автоматична класифікація крос-звʼязків, генерація описів '
            'та аналітика залишків).'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 0,
        'title': '1-й платіж (50%)',
        'body': (
            'Вноситься як авансовий платіж перед стартом проєктування та розробки.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.PAYMENT,
        'order': 1,
        'title': '2-й платіж (50%)',
        'body': (
            'Вноситься після фінального тестування, демонстрації працездатності системи, '
            'перед деплоєм на робочий сервер та передачею всіх доступів.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 0,
        'title': 'Крос-таблиця сумісності — нормалізована модель Fitment',
        'body': (
            'Окремий звʼязок part ↔ vehicle modification з composite-індексами. '
            'Не M2M «в лоб»: на 100k+ SKU підбір по авто деградує за секунди. '
            'Fitment дає стабільні JOIN і кешовані вибірки по марці/моделі/року.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 1,
        'title': 'Пошук по крос-кодах — нормалізація + GIN/trigram',
        'body': (
            'Артикули нормалізуються (upper, без дефісів/пробілів) у окреме поле. '
            'Пошук через PostgreSQL GIN / trigram, а не LIKE \'%code%\'. '
            'Інакше каталог з аналогами стає вузьким місцем під навантаженням.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 2,
        'title': 'B2B-ціни — прайс-колонки + Redis по групі клієнта',
        'body': (
            'Індивідуальні оптові колонки зберігаються на рівні групи клієнта. '
            'Перерахунок — фоновий job, у запиті — кеш Redis по групі. '
            'Ніколи не рахувати знижки на льоту для кожного SKU у списку.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 3,
        'title': 'XML/YML фіди — генерація за розкладом, не з БД на льоту',
        'body': (
            'Prom.ua / Rozetka фіди збираються cron-ом у статичні файли, '
            'віддаються через nginx. Генерація «на запит» з повної номенклатури '
            'гарантовано вбʼє воркер під піком оновлень каталогу.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 4,
        'title': 'Кредитні ліміти — транзакційний ledger',
        'body': (
            'Баланс — агрегат з журналу операцій, не «поточне поле» на клієнті. '
            'Акти звірки та акти видачі рахуються з ledger. '
            'Так уникаємо розсинхрону після часткових оплат і повернень.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 5,
        'title': 'Ролі — Django permissions + scoped-ролі в B2B-кабінеті',
        'body': (
            'Глобальні права через Django permissions; права партнера — '
            'обʼєктні ролі в межах його кабінету. Ніяких if username == ... '
            'у views — інакше аудит доступу неможливий.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 6,
        'title': 'Поетапна здача на staging з реальним дампом',
        'body': (
            'Каталог+B2C → B2B-кабінети+ціни → фіди+акти → AI. '
            'Кожен етап приймається на staging з повним дампом номенклатури клієнта, '
            'не на демо-даних із 200 товарів.'
        ),
    },
    {
        'kind': ProposalSpec.Kind.RECOMMENDATION,
        'order': 7,
        'title': 'Навантаження — Redis-дерево + prefetch-аудит',
        'body': (
            'Категорійне дерево і фасетні фільтри — у Redis. '
            'Перед релізом — аудит select_related/prefetch і PageSpeed 90+ '
            'на повній базі. Демо-набір ніколи не показує реальні вузькі місця.'
        ),
    },
]

INTRO_HTML = """
<p><strong>PrometeyLabs</strong> — це команда, де досвідчені розробники та маркетологи працюють як єдиний механізм. Ми будуємо готові масштабовані цифрові екосистеми з глибокою автоматизацією гуртової та роздрібної торгівлі, оптимізовані під високі навантаження та складну бізнес-логіку.</p>
<p>Ми відмовляємося від шаблонних CMS і конструкторів, які не витримують великої номенклатури. Кастомне рішення: <strong>Django / HTML5 / HTMX / CSS3 / JavaScript</strong> з кешуванням Redis та базою PostgreSQL.</p>
<ul>
<li><strong>Блискавична швидкість (PageSpeed 90+)</strong> — миттєве завантаження категорій і сотень тисяч модифікацій запчастин.</li>
<li><strong>Enterprise-безпека</strong> — захист комерційних даних, індивідуальних прайсів, договорів та звірок.</li>
<li><strong>Повна свобода та масштабованість</strong> — без обмежень платних плагінів, інтеграція будь-яких API-шлюзів і маркетплейсів.</li>
</ul>
""".strip()

GUARANTEE_HTML = """
<p>Ми впевнені у якості нашого коду. Оскільки система розробляється з нуля без використання сторонніх CMS-модулів, вона не потребує щомісячних оновлень, які часто ламають звичайні сайти.</p>
<p>Ми надаємо <strong>ПОЖИТТЄВУ ГАРАНТІЮ</strong> на стабільність роботи нашого коду протягом усього періоду експлуатації ресурсу.</p>
""".strip()


def _with_ru(payload: dict, text_keys: tuple[str, ...]) -> dict:
    """UA → RU/EN/CS для seed-записів.

    RU автоперекладається правило-based (`translate_ua_to_ru`), якщо не задано вручну.
    EN/CS автоперекладу не мають (немає правило-based перекладача) — просто
    прокидаються з payload, якщо там вже є `<key>_en`/`<key>_cs` (додайте їх у
    словник MODULES/PACKAGES/SPECS і після push+redeploy вони підхопляться сідом).
    За відсутності — лишаються порожніми, `localized_text()` фолбечиться на UA.
    """
    out = dict(payload)
    for key in text_keys:
        ru_key = f'{key}_ru'
        if ru_key not in out:
            out[ru_key] = translate_ua_to_ru(out.get(key, ''))
        for lang in ('en', 'cs'):
            lang_key = f'{key}_{lang}'
            out.setdefault(lang_key, '')
    return out


def _attach_hero(proposal: Proposal) -> None:
    src = Path(settings.BASE_DIR) / 'static' / 'proposal' / 'img' / 'parts.png'
    if not src.is_file():
        return
    if proposal.hero_image:
        proposal.hero_image.delete(save=False)
    with src.open('rb') as handle:
        proposal.hero_image.save('hero.png', File(handle), save=True)


class Command(BaseCommand):
    help = 'Seed B2B parts platform commercial proposal (idempotent)'

    @transaction.atomic
    def handle(self, *args, **options):
        proposal, created = Proposal.objects.update_or_create(
            slug=SLUG,
            defaults={
                'client_name': 'B2B Parts Platform',
                'title': (
                    'Розробка високопродуктивної B2B / B2C E-Commerce '
                    'платформи автозапчастин під ключ'
                ),
                'title_ru': (
                    'Разработка высокопроизводительной B2B / B2C E-Commerce '
                    'платформы автозапчастей под ключ'
                ),
                # EN/CS — заповніть при потребі, поки фолбек на UA (localized_text)
                'title_en': '',
                'title_cs': '',
                'lead': (
                    'Кастомна платформа на Django / HTMX / PostgreSQL / Redis '
                    'для гуртової та роздрібної торгівлі автозапчастинами.'
                ),
                'lead_ru': (
                    'Кастомная платформа на Django / HTMX / PostgreSQL / Redis '
                    'для оптовой и розничной торговли автозапчастями.'
                ),
                'lead_en': 'Custom platform on Django / HTMX / PostgreSQL / Redis for wholesale and retail trade of auto parts.',
                'lead_cs': 'Customizovaná platforma na Django / HTMX / PostgreSQL / Redis pro velkoobchodní a maloobchodní prodej autodílů.',
                'recommendations_lead': RECS_LEAD,
                'recommendations_lead_ru': translate_ua_to_ru(RECS_LEAD),
                'recommendations_lead_en': '',
                'recommendations_lead_cs': '',
                'issued_on': date(2026, 8, 20),
                'intro_html': INTRO_HTML,
                'intro_html_ru': translate_ua_to_ru(INTRO_HTML),
                'intro_html_en': '',
                'intro_html_cs': '',
                'guarantee_html': GUARANTEE_HTML,
                'guarantee_html_ru': translate_ua_to_ru(GUARANTEE_HTML),
                'guarantee_html_en': '',
                'guarantee_html_cs': '',
                'cta_label': 'Обговорити проєкт',
                'cta_label_ru': 'Обсудить проект',
                'cta_label_en': '',
                'cta_label_cs': '',
                'is_published': True,
                'order': 0,
            },
        )

        proposal.modules.all().delete()
        for data in MODULES:
            ProposalModule.objects.create(
                proposal=proposal,
                **_with_ru(data, ('title', 'description')),
            )

        proposal.packages.all().delete()
        for data in PACKAGES:
            ProposalPackage.objects.create(
                proposal=proposal,
                **_with_ru(data, ('name', 'scope', 'duration')),
            )

        proposal.specs.all().delete()
        for data in SPECS:
            ProposalSpec.objects.create(
                proposal=proposal,
                **_with_ru(data, ('title', 'body')),
            )

        proposal.highlights.all().delete()
        for data in HIGHLIGHTS:
            ProposalHighlight.objects.create(
                proposal=proposal,
                **_with_ru(data, ('title',)),
            )

        proposal.arch_nodes.all().delete()
        for data in ARCH_NODES:
            ProposalArchNode.objects.create(
                proposal=proposal,
                **_with_ru(data, ('title', 'caption')),
            )

        _attach_hero(proposal)

        action = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(
            f'{action}: /proposal/{SLUG}/ '
            f'({proposal.modules.count()} modules, '
            f'{proposal.packages.count()} packages, '
            f'{proposal.specs.count()} specs, '
            f'{proposal.highlights.count()} highlights, '
            f'{proposal.arch_nodes.count()} arch nodes)'
        ))
