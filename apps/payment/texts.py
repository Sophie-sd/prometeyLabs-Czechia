"""Public texts for the .cz payment page and the invoice PDF (CS + EN).

Defaults live here; every key can be overridden in admin via ``PaymentText``
(Платежі → Тексти оплати і PDF). Empty DB value → default is used.
Placeholders in ``{curly}`` braces are filled in code.
"""
from __future__ import annotations

from django.utils import translation

LANGS = ('cs', 'en')

# key: (admin hint, CS default, EN default)
DEFAULT_TEXTS = {
    # ── Payment page: general ────────────────────────────────────────────
    'browser_title': ('Заголовок вкладки браузера', 'Platba', 'Payment'),
    'page_title': ('Заголовок сторінки оплати', 'Platba za služby', 'Payment for services'),
    'secured': ('Позначка «захищено» у шапці', 'Zabezpečeno', 'Secured'),
    'amount_label': ('Підпис суми', 'Částka k úhradě', 'Amount due'),
    'countdown_label': ('Підпис таймера', 'Čas na úhradu', 'Time left to pay'),
    'countdown_expired': ('Таймер: час вийшов', 'ČAS VYPRŠEL', 'TIME IS UP'),
    'documents_label': ('Заголовок блоку документів', 'Dokumenty', 'Documents'),
    'doc_contract': ('Тип документа: договір', 'Smlouva', 'Contract'),
    'doc_invoice': ('Тип документа: рахунок', 'Faktura', 'Invoice'),
    'doc_other': ('Тип документа: інший', 'Dokument', 'Document'),
    'doc_default_contract': ('Типовий договір', 'Vzorová smlouva', 'Standard contract'),
    'executor_label': ('Блок виконавця на сторінці', 'Poskytovatel', 'Executor'),
    'reg_no_label': ('Підпис реєстраційного номера', 'Registrační číslo', 'Registration No.'),
    # ── Consent (§1837 NOZ) ──────────────────────────────────────────────
    'consent_title': (
        'Заголовок блоку згоди',
        'Před zobrazením platebních údajů prosím potvrďte:',
        'Before the payment details are shown, please confirm:',
    ),
    'consent_withdrawal': (
        'Чекбокс: відмова від 14-денного відступлення',
        'Potvrzuji, že objednávám službu individuálního vývoje / souhlasím se zahájením plnění '
        'před uplynutím lhůty pro odstoupení, a ztrácím 14denní právo na odstoupení od smlouvy '
        '(čl. 16(a)/(c) směrnice 2011/83/EU, §1837 písm. a)/l) NOZ).',
        'I confirm that I am ordering a custom development service / agree to start performance '
        'before the withdrawal period ends, and I lose the 14-day right of withdrawal '
        '(Art. 16(a)/(c) Directive 2011/83/EU, §1837(a)/(l) Czech Civil Code).',
    ),
    'consent_data': (
        'Чекбокс: згода на обробку даних ({privacy_link} — посилання)',
        'Souhlasím se zpracováním osobních údajů pro účely této platby v souladu se {privacy_link}.',
        'I consent to personal data processing for this payment under the {privacy_link}.',
    ),
    'consent_privacy_link': (
        'Текст посилання на політику конфіденційності',
        'Zásadami ochrany osobních údajů', 'Privacy Policy',
    ),
    'consent_button': (
        'Кнопка підтвердження згоди',
        'Potvrdit a zobrazit platební údaje', 'Confirm and show payment details',
    ),
    'consent_confirmed': ('Після підтвердження', 'Podmínky byly potvrzeny.', 'Terms confirmed.'),
    'consent_error': (
        'Помилка: не відмічено чекбокси',
        'Potvrďte prosím oba body: vzdání se práva na odstoupení a souhlas se zpracováním údajů.',
        'Please confirm both items: the waiver of the right of withdrawal and the consent to data processing.',
    ),
    'details_hidden_hint': (
        'Підказка до згоди',
        'Platební údaje se zobrazí po potvrzení obou bodů.',
        'The payment details will be shown after you confirm both items.',
    ),
    # ── Payment details ──────────────────────────────────────────────────
    'details_label': ('Заголовок реквізитів', 'Platební údaje', 'Payment details'),
    'field_beneficiary': ('Поле: отримувач', 'Příjemce', 'Beneficiary'),
    'field_iban': ('Поле: IBAN', 'IBAN', 'IBAN'),
    'field_swift': ('Поле: SWIFT/BIC', 'SWIFT/BIC', 'SWIFT/BIC'),
    'field_bank': ('Поле: банк', 'Banka', 'Bank'),
    'field_beneficiary_address': ('Поле: адреса отримувача', 'Adresa příjemce', 'Beneficiary address'),
    'field_paypal_email': ('Поле: PayPal email', 'PayPal e-mail', 'PayPal email'),
    'field_purpose': ('Поле: призначення платежу', 'Účel platby', 'Payment purpose'),
    'field_amount': ('Поле: сума', 'Částka', 'Amount'),
    'method_sepa_eur': ('Назва способу SEPA EUR', 'Bankovní převod SEPA (EUR)', 'SEPA bank transfer (EUR)'),
    'method_swift_eur': ('Назва способу SWIFT EUR', 'Mezinárodní převod SWIFT (EUR)', 'SWIFT international transfer (EUR)'),
    'method_swift_usd': ('Назва способу SWIFT USD', 'Mezinárodní převod SWIFT (USD)', 'SWIFT international transfer (USD)'),
    'method_paypal': ('Назва способу PayPal', 'PayPal', 'PayPal'),
    'copy': ('Кнопка копіювання рядка', 'Kopírovat', 'Copy'),
    'copy_details': ('Кнопка копіювання блоку реквізитів', 'Kopírovat platební údaje', 'Copy payment details'),
    'copied': ('Після копіювання', '✓ Zkopírováno', '✓ Copied'),
    'paypal_button': ('Кнопка PayPal', 'Zaplatit přes PayPal', 'Pay with PayPal'),
    'howto_label': ('Заголовок «Як оплатити»', 'Jak zaplatit', 'How to pay'),
    'howto_text': (
        'Текст «Як оплатити»',
        'Uhraďte částku převodem podle platebních údajů výše a uveďte účel platby. '
        'Po úhradě nám prosím pošlete potvrzení o platbě:',
        'Pay the amount by transfer using the payment details above and include the payment purpose. '
        'After paying, please send us the payment confirmation:',
    ),
    'telegram_button': ('Кнопка Telegram', 'Napsat na Telegram', 'Message us on Telegram'),
    'telegram_url': ('Посилання Telegram', 'https://t.me/prometeylabs', 'https://t.me/prometeylabs'),
    # ── Footer ───────────────────────────────────────────────────────────
    'footer_site_label': ('Футер: назва сайту', 'prometeylabs.cz', 'prometeylabs.cz'),
    'footer_site_url': ('Футер: URL сайту', 'https://prometeylabs.cz', 'https://prometeylabs.cz/en/'),
    'footer_offer': ('Футер: оферта', 'Veřejná nabídka (smlouva)', 'Public Agreement (Offer)'),
    'footer_privacy': ('Футер: конфіденційність', 'Ochrana soukromí', 'Privacy Policy'),
    'footer_cookies': ('Футер: cookies', 'Cookies', 'Cookies'),
    'footer_refund': ('Футер: повернення коштів', 'Vrácení peněz', 'Refund Policy'),
    'footer_ip': ('Футер: інтелектуальна власність', 'Duševní vlastnictví', 'Intellectual Property'),
    # ── Status pages ─────────────────────────────────────────────────────
    'inactive_title': ('Посилання неактивне: заголовок', 'Nedostupné', 'Unavailable'),
    'inactive_text': (
        'Посилання неактивне: текст',
        'Tento platební odkaz již není aktivní.', 'This payment link is no longer active.',
    ),
    'inactive_paid_text': (
        'Посилання вже оплачене: текст',
        'Tento platební odkaz již byl uhrazen. Děkujeme!', 'This payment link has already been paid. Thank you!',
    ),
    'success_title': ('Успішна оплата: заголовок', 'Děkujeme!', 'Thank you!'),
    'success_text': (
        'Успішна оплата: текст',
        'Platba byla úspěšná. Potvrzení jsme již obdrželi.', 'Payment completed successfully.',
    ),
    'success_waiver': (
        'Успішна оплата: текст про §1824a NOZ',
        'Podle §1824a NOZ a čl. 16 směrnice 2011/83/EU jste ztratili 14denní právo na odstoupení '
        'od smlouvy, protože jste výslovně předem souhlasili se zahájením plnění individuální služby.',
        'Under §1824a of the Czech Civil Code and Art. 16 of Directive 2011/83/EU you have lost the '
        '14-day right of withdrawal, because you gave prior express consent to start performing a custom service.',
    ),
    'failure_title': ('Помилка оплати: заголовок', 'Chyba', 'Error'),
    'failure_text': (
        'Помилка оплати: текст',
        'Platbu se nepodařilo provést. Zkuste to prosím znovu nebo nás kontaktujte.',
        'The payment could not be completed. Please try again or contact us.',
    ),
    'online_unavailable': (
        'Відповідь, якщо хтось звертається до старої онлайн-оплати',
        'Online platba není k dispozici. Použijte prosím platební údaje na stránce.',
        'Online payment is not available. Please use the payment details on the page.',
    ),
    'email_subject': ('Лист: тема', 'Potvrzení platby — PrometeyLabs', 'Payment confirmation — PrometeyLabs'),
    'email_thanks': ('Лист: подяка', 'Děkujeme za platbu.', 'Thank you for your payment.'),
    # ── Invoice PDF ──────────────────────────────────────────────────────
    'pdf_title': ('PDF: заголовок', 'Faktura / Akt o poskytnutých službách', 'Invoice / Act of services rendered'),
    'pdf_number': ('PDF: номер', 'Číslo', 'No.'),
    'pdf_issue_date': ('PDF: дата виставлення', 'Datum vystavení', 'Issue date'),
    'pdf_due_date': ('PDF: термін оплати', 'Datum splatnosti', 'Due date'),
    'pdf_executor': ('PDF: виконавець', 'Poskytovatel', 'Executor'),
    'pdf_customer': ('PDF: замовник', 'Objednatel', 'Customer'),
    'pdf_company_id': ('PDF: IČO / Company ID', 'IČO', 'Company ID'),
    'pdf_vat_id': ('PDF: DIČ / VAT ID', 'DIČ', 'VAT ID'),
    'pdf_reg_no': ('PDF: реєстраційний номер виконавця', 'Registrační číslo', 'Registration No.'),
    'pdf_email': ('PDF: email', 'E-mail', 'Email'),
    'pdf_country': ('PDF: країна', 'Země', 'Country'),
    'pdf_contract': ('PDF: заголовок «Договір»', 'Smlouva', 'Contract'),
    'pdf_contract_line': (
        'PDF: рядок договору ({number}, {date})',
        'Smlouva č. {number} ze dne {date}', 'Contract No. {number} dated {date}',
    ),
    'pdf_services': ('PDF: заголовок послуг', 'Služby', 'Services'),
    'pdf_col_no': ('PDF: колонка №', 'Č.', 'No.'),
    'pdf_col_service': ('PDF: колонка послуга', 'Popis služby', 'Service'),
    'pdf_col_unit': ('PDF: колонка од.', 'Jedn.', 'Unit'),
    'pdf_col_qty': ('PDF: колонка к-сть', 'Počet', 'Qty'),
    'pdf_col_price': ('PDF: колонка ціна', 'Cena', 'Price'),
    'pdf_col_amount': ('PDF: колонка сума', 'Částka', 'Amount'),
    'pdf_unit_default': ('PDF: одиниця за замовчуванням', 'služba', 'service'),
    'pdf_total': ('PDF: разом до сплати', 'Celkem k úhradě', 'Total due'),
    'pdf_in_words': ('PDF: сума прописом', 'Slovy', 'In words'),
    'pdf_payment_details': ('PDF: платіжні реквізити', 'Platební údaje', 'Payment details'),
    'pdf_purpose': ('PDF: призначення платежу', 'Účel platby', 'Payment purpose'),
    'pdf_signature': ('PDF: підпис', 'Poskytovatel', 'Executor'),
    'pdf_page_footer': (
        'PDF: нижній колонтитул ({email}, {website})',
        'PrometeyLabs · {email} · {website}', 'PrometeyLabs · {email} · {website}',
    ),
    'pdf_footer_note': (
        'PDF: примітка внизу (ПДВ / акт)',
        'DPH není účtována.\nTato faktura slouží zároveň jako akt o poskytnutých službách. '
        'Úhradou faktury Objednatel potvrzuje, že služby byly poskytnuty v plném rozsahu '
        'a nemá výhrady k jejich rozsahu, kvalitě ani termínu.',
        'VAT is not charged.\nThis invoice also serves as the act of services rendered. '
        'Payment of this invoice confirms that the services have been provided in full and that '
        'the Customer has no claims regarding their scope, quality or timing.',
    ),
    'purpose_template': (
        'Призначення платежу ({service}, {number}, {date})',
        'Platba za {service} dle faktury č. {number} ze dne {date}',
        'Payment for {service} by the invoice № {number} from {date}',
    ),
}


def normalize_lang(lang: str | None) -> str:
    lang = (lang or '').split('-')[0].lower()
    return lang if lang in LANGS else 'cs'


def current_lang() -> str:
    return normalize_lang(translation.get_language())


def default_text(key: str, lang: str) -> str:
    entry = DEFAULT_TEXTS.get(key)
    if not entry:
        return ''
    return entry[2] if normalize_lang(lang) == 'en' else entry[1]


def get_texts(lang: str | None = None) -> dict:
    """All texts for ``lang`` (defaults overridden by non-empty DB values)."""
    lang = normalize_lang(lang or current_lang())
    texts = {key: default_text(key, lang) for key in DEFAULT_TEXTS}
    try:
        from .models import PaymentText
        field = 'text_en' if lang == 'en' else 'text_cs'
        for key, value in PaymentText.objects.values_list('key', field):
            if key in texts and (value or '').strip():
                texts[key] = value
    except Exception:  # table missing during early migrations
        pass
    return texts
