"""
Ключі відповідей квізів v2 (internet-shop-v2 / corporate-website-v2).

У формах value радіо/чекбоксів — латинські ключі; для CRM (KeyCRM manager_comment)
ключі перетворюються на людські назви (мова менеджерів — українська, як решта
службових рядків картки). Старі кириличні value (кешований HTML) мапляться на ті
самі ключі через LEGACY_VALUE_TO_KEY.
"""

QUIZ_FIELDS = {
    'q_start': ('Старт проєкту', {
        'scratch': 'Старт з нуля',
        'migration': 'Міграція з Prom / OLX',
        'scale_marketing': 'Масштабування + маркетинг під ключ',
        'undecided': 'Ще не визначився',
    }),
    'q_products': ('Кількість товарів', {
        'up_to_100': 'До 100 товарів',
        '100_1000': '100–1000 товарів',
        '1000_10000': '1000–10 000 товарів',
        'over_10000': 'Більше 10 000 товарів',
    }),
    'q_features': ('Додаткові опції', {
        'crm_telegram': 'CRM + Telegram',
        'seo_articles': 'SEO + статті',
        'ai_admin_bot': 'AI-адмінка + бот',
        'ads_promotion': 'Реклама та просування',
    }),
    'q_business': ('Тип бізнесу', {
        'services': 'Послуги (B2C / B2B)',
        'manufacturing': 'Виробництво / опт',
        'trade': 'Торгівля',
        'other': 'Інше / не визначився',
    }),
    'q_goal': ('Бізнес-ціль', {
        'leads': 'Збір заявок та контактів',
        'online_sales': 'Прямі онлайн-продажі',
        'brand': 'Презентація бренду або послуг',
        'scaling': 'Масштабування',
    }),
    'q_pages': ('Кількість сторінок', {
        'landing': '1 сторінка (лендінг)',
        'up_to_10': 'до 10 сторінок',
        '11_20': '11–20 сторінок',
        '21_plus': '21+ сторінок',
    }),
    'q_options': ('Додаткові опції', {
        'ads': 'Рекламні послуги',
        'seo': 'SEO розвиток сайту',
        'crm_automation': 'CRM та автоматизація',
        'multilang': 'Мультимовність',
    }),
    # Спільне поле обох квізів (e-shop: 2 тижні / 1–3 міс.; corporate: 7 днів / 2 тижні).
    'q_timeline': ('Терміни', {
        'asap_2w': 'Якнайшвидше (до 2 тижнів)',
        'asap_7d': 'Якнайшвидше (до 7 днів)',
        'within_2w': 'Протягом 2 тижнів',
        'within_month': 'Протягом місяця',
        '1_3_months': '1–3 місяці',
        'flexible': 'Терміни гнучкі',
    }),
}

# Старі кириличні value → ключ (зворотна сумісність).
LEGACY_VALUE_TO_KEY = {
    field: {label: key for key, label in options.items()}
    for field, (_title, options) in QUIZ_FIELDS.items()
}
LEGACY_VALUE_TO_KEY['q_pages']['1 сторінка (лендинг)'] = 'landing'

MAX_RAW_LEN = 100


def normalize_quiz_value(field, value):
    """Ключ для значення поля; невідоме значення повертається як є (обрізане)."""
    value = (value or '').strip()
    if not value or field not in QUIZ_FIELDS:
        return ''
    options = QUIZ_FIELDS[field][1]
    if value in options:
        return value
    legacy = LEGACY_VALUE_TO_KEY.get(field, {}).get(value)
    if legacy:
        return legacy
    return value[:MAX_RAW_LEN]


def extract_quiz_answers(post):
    """{поле: [ключі]} з POST (QueryDict) лише для відомих q_* полів."""
    answers = {}
    for field in QUIZ_FIELDS:
        values = [normalize_quiz_value(field, v) for v in post.getlist(field)]
        values = [v for v in values if v]
        if values:
            answers[field] = values
    return answers


def quiz_answer_label(field, key):
    options = QUIZ_FIELDS.get(field, ('', {}))[1]
    return options.get(key, key)


def format_quiz_answers(answers):
    """Рядки для CRM: «Терміни: Терміни гнучкі»."""
    lines = []
    for field, (title, _options) in QUIZ_FIELDS.items():
        keys = (answers or {}).get(field)
        if not keys:
            continue
        if isinstance(keys, str):
            keys = [keys]
        lines.append(f'{title}: ' + ', '.join(quiz_answer_label(field, k) for k in keys))
    return lines


# ---------------------------------------------------------------------------
# Службові ключі форм v2 (data-source-label, приховані details/name).
# У HTML/JS — лише латинські ключі; людські назви для менеджера — тут.
# ---------------------------------------------------------------------------

SOURCE_LABELS = {
    'corporate_website_v2': 'Корпоративний сайт v2',
    'internet_shop_v2': 'Інтернет-магазин v2',
    'internet_shop_v2_hero': 'Інтернет-магазин v2 · Форма на першому екрані',
}

LEGACY_SOURCE_TO_KEY = {label: key for key, label in SOURCE_LABELS.items()}
LEGACY_SOURCE_TO_KEY.update({
    'Інтернет-магазин v2 · перший екран': 'internet_shop_v2_hero',
    'Корпоративний сайт': 'corporate_website_v2',
})

# Ключі рядків у details, які збирає JS квізу: «ключ: значення».
DETAIL_LINE_LABELS = {
    'page': 'Сторінка',
    'package': 'Рекомендований пакет',
    'pkg_hint': 'Підказка з картки пакета',
}

# Приховане поле name у формах без поля імені → назва ліда для картки CRM.
# Заголовок картки: «<тип форми (cs)> - <назва>», тому назва — чеською.
LEAD_NAME_PLACEHOLDERS = {
    'free_analysis': 'Bezplatná analýza',
}
LEGACY_NAME_TO_KEY = {
    'Безкоштовний аналіз': 'free_analysis',
}


def source_label(value):
    value = (value or '').strip()
    key = value if value in SOURCE_LABELS else LEGACY_SOURCE_TO_KEY.get(value)
    return SOURCE_LABELS[key] if key else value


def resolve_lead_name(name):
    """Ключ-заглушка (або стара кирилична заглушка) → назва для CRM; інше без змін."""
    name = (name or '').strip()
    key = name if name in LEAD_NAME_PLACEHOLDERS else LEGACY_NAME_TO_KEY.get(name)
    return LEAD_NAME_PLACEHOLDERS[key] if key else name


def humanize_details(details):
    """
    Рядки «ключ: значення» з JS квізу → людські назви для менеджера.
    Невідомі рядки (у т.ч. старий кириличний формат) лишаються як є.
    """
    if not details:
        return details
    out = []
    for line in details.splitlines():
        key, sep, value = line.partition(':')
        key = key.strip()
        value = value.strip()
        if not sep:
            out.append(line)
        elif key == 'page':
            out.append(f"{DETAIL_LINE_LABELS['page']}: {source_label(value)}")
        elif key in DETAIL_LINE_LABELS:
            out.append(f'{DETAIL_LINE_LABELS[key]}: {value}')
        elif key in QUIZ_FIELDS:
            labels = [
                quiz_answer_label(key, normalize_quiz_value(key, part))
                for part in value.split(',') if part.strip()
            ]
            out.append(f'{QUIZ_FIELDS[key][0]}: ' + ', '.join(labels))
        else:
            out.append(line)
    return '\n'.join(out)
