"""SSOT: помаранчева кнопка-квіз «Spočítat…» на посадкових (cs/en).

Одна дія на першому екрані; мікротекст = що буде після натиску.
Ніде не обіцяємо «ціну одразу» чи «без дзвінка» — телефон квіз просить у кінці.

target:
  * '#…'         — квіз на цій самій сторінці;
  * 'calculator' — /calculator/ з автостартом тесту.
"""

CALC_CTA = {
    'home': {
        'target': 'calculator',
        'cs': {
            'label': 'Spočítat cenu webu',
            'micro': '5 otázek · 2 minuty · zdarma, bez závazků',
        },
        'en': {
            'label': 'Calculate website cost',
            'micro': '5 questions · 2 minutes · free, no obligation',
        },
    },
    # Kvíz je vložený přímo na stránce (#pl-rs-calc); sticky i na desktopu,
    # bez šipky, s vlastní událostí sticky_cta_click (není to konverze).
    'rozrobka': {
        'target': '#pl-rs-calc',
        'sticky_desktop': True,
        'sticky_arrow': False,
        'sticky_event': 'sticky_cta_click',
        'cs': {
            'label': 'Spočítat cenu online',
            'sticky': 'Spočítejte cenu online',
            'micro': '5 otázek · 2 minuty · zdarma, bez závazků',
        },
        'en': {
            'label': 'Calculate the price online',
            'sticky': 'Calculate the price online',
            'micro': '5 questions · 2 minutes · free, no obligation',
        },
    },
    'shop': {
        'target': '#calculator',
        'cs': {
            'label': 'Spočítat cenu e-shopu',
            'sticky': 'Spočítat cenu e-shopu',
            'micro': '4 otázky · 1 minuta · vybereme balíček od 34 500 Kč',
        },
        'en': {
            'label': 'Calculate store cost',
            'sticky': 'Calculate store cost',
            'micro': '4 questions · 1 minute · we pick a package from CZK 34,500',
        },
    },
    'corp': {
        'target': '#calculator',
        'cs': {
            'label': 'Spočítat cenu webu',
            'micro': '5 otázek · 2 minuty · vybereme balíček pro váš byznys',
        },
        'en': {
            'label': 'Calculate website cost',
            'micro': '5 questions · 2 minutes · we pick a package for your business',
        },
    },
    'dorobka': {
        'target': 'calculator',
        'cs': {
            'label': 'Spočítat cenu úprav',
            'micro': '5 otázek · 2 minuty · zdarma, bez závazků',
        },
        'en': {
            'label': 'Calculate the work cost',
            'micro': '5 questions · 2 minutes · free, no obligation',
        },
    },
}

CALC_START_QUERY = '?start=1'


def calc_cta_copy(page, lang):
    """Return {'label', 'sticky', 'micro', 'target', 'sticky_*'} for page × lang (cs fallback)."""
    entry = CALC_CTA[page]
    lang = 'en' if (lang or '').startswith('en') else 'cs'
    data = dict(entry[lang])
    data['target'] = entry['target']
    # sticky options (shared component): defaults = mobile-only bar with arrow, cta_calc_click
    data['sticky_desktop'] = entry.get('sticky_desktop', False)
    data['sticky_arrow'] = entry.get('sticky_arrow', True)
    data['sticky_event'] = entry.get('sticky_event', '')
    data.setdefault('sticky', data['label'])
    return data
