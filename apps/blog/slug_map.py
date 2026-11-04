"""CZ blog: old Ukrainian-transliteration slugs → Czech slugs (2026-11-04).

Used by the 301 route (apps/blog/urls.py) and data migration 0005. Same Czech slug on /blog/ and /en/blog/.
"""
OLD_TO_NEW = {
    'majbutne-veb-rozrobky-prohnoz-cherez-2-3-roky': 'budoucnost-weboveho-vyvoje-prognoza',
    'pwa-sajt-chy-dodatok-chomu-krashche-mobilnoho': 'pwa-nebo-mobilni-aplikace',
    'avtomatyzatsiya-marketyngu-yak-ai-zaminyv-3-marketolohiv': 'automatizace-marketingu-ai-nahradila-marketery',
    'ai-v-internet-magazyni-yak-pidnyaly-serednij-chek': 'ai-e-shop-prumerna-objednavka',
    'bezpeka-saytu-istoriya-zlomu-400000-zbytkiv': 'bezpecnost-webu-pribeh-pruniku',
    'mobilna-versiya-chому-67-kliyentiv-vidvalyvalys': 'mobilni-verze-webu-odchod-klientu',
    'mvp-za-4-tyzhni-istoriya-startapu-shcho-zaluchyv-investytsiyi': 'mvp-4-tydny-startup-investice',
    'ai-spivrobitnyk-koly-shtuchnyj-intelekt-najnyaly-na-robotu': 'ai-zamestnanci-umela-inteligence-prace',
    'seo-z-ai-yak-vyjty-v-top-google-za-2-misyatsi': 'seo-ai-top-3-google-2-mesice',
    'ai-chat-boty-koly-kliyent-ne-rozumiye-shcho-spilkuyetsya': 'ai-chatboti-klient-nepozna-bota',
    'telegram-boty-dlya-biznesu-chomu-vlasnyk-kaviярні-zvilnyv': 'telegram-boty-byznys-kavarna-administrator',
    'skilky-koshtuye-zrobyty-sajt-v-ukrayini-realni-tsiny': 'kolik-stoji-web-cesko-ceny',
    'api-intehratsii-yak-obyednaty-systemy-biznesu': 'api-integrace-propojeni-firemnich-systemu',
    'ai-u-veb-rozrobtsi-yak-shtuchnyj-intelekt-zminyuye-stvorennya-sajtiv': 'ai-webovy-vyvoj-tvorba-webu',
}


def replace_old_slugs(text):
    """Rewrite /blog/<old>/ links (raw and percent-encoded Cyrillic) inside HTML/text."""
    if not text:
        return text
    from urllib.parse import quote
    for old, new in OLD_TO_NEW.items():
        for variant in {old, quote(old, safe='-')}:
            text = text.replace('/blog/' + variant, '/blog/' + new)
    return text
