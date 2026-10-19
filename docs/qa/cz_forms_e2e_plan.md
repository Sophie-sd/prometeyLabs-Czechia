# План e2e-тестування форм prometeylabs.cz (п.78)

Статус: **план + локальний smoke через Django test client** (KeyCRM замокано).
Живий сайт і живий KeyCRM у цьому плані **не використовуються**. Усі тестові ліди
мають ім'я/повідомлення з префіксом `TEST` і e-mail `test@example.com`.

Гілка: `cz/integrations` (п.12 додає `site`/`lang` у кожен лід).

---

## 0. Як запускати локально без живого KeyCRM

### Що вже існує в коді (stub-режим)
- `KEYCRM_API_KEY` порожній → `KeyCRMService.is_configured == False` →
  `sync_submission_to_keycrm()` нічого не шле (лог `KeyCRM API key not configured`).
  У worktree `.env` **відсутній**, тому за замовчуванням KeyCRM вимкнено.
- Окремого прапорця «stub / dry-run» для KeyCRM **немає** — вимкнення = порожній ключ.
- `EMAIL_BACKEND` у `config/settings.py` **захардкоджено як SMTP** (змінна
  `EMAIL_BACKEND` з `.env.example` не читається). Під runserver лист спробує піти
  через `smtp.gmail.com` і впаде (у фоновому потоці, на відповідь форми не впливає).

### Варіант A — автотести (рекомендовано, без мережі)
```bash
cd ~/Sites/cz-wt-integrations
~/Sites/prometeyLabs-Czechia/.venv/bin/python manage.py compilemessages -l cs -l en   # .mo в .gitignore
env -u DATABASE_URL KEYCRM_API_KEY= \
  ~/Sites/prometeyLabs-Czechia/.venv/bin/python manage.py test \
  apps.core.tests.test_keycrm_lead_tags apps.core.tests.test_forms apps.core.tests.test_cta_channels
```
Test runner підміняє e-mail на locmem; KeyCRM `requests.post` замокано в тестах.

### Варіант B — ручний runserver
Локальний файл налаштувань (НЕ комітити), напр. `/tmp/e2e_settings.py` або
`config/settings_e2e_local.py` (додати в `.git/info/exclude`):
```python
from config.settings import *  # noqa
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
KEYCRM_API_KEY = ''                      # KeyCRM вимкнено: жодного HTTP
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': '/tmp/cz_e2e.sqlite3'}}
```
```bash
env -u DATABASE_URL ~/Sites/prometeyLabs-Czechia/.venv/bin/python manage.py migrate --settings=config.settings_e2e_local
env -u DATABASE_URL ~/Sites/prometeyLabs-Czechia/.venv/bin/python manage.py runserver 127.0.0.1:8000 --settings=config.settings_e2e_local
```
Перевірка KeyCRM-payload без мережі: в `manage.py shell` замокати
`apps.core.keycrm_service.requests.post` і викликати
`KeyCRMService().create_pipeline_card(FormSubmission.objects.latest('id'))`
з `settings.KEYCRM_API_KEY='test'` (див. `apps/core/tests/test_keycrm_lead_tags.py`).

### Перевірка на staging/проді (лише після рішення Олега)
Тільки окремим тестовим pipeline/ключем KeyCRM або з подальшим ручним
архівуванням карток `TEST`. Конверсії Google Ads (п.77) — **не чіпати**.

---

## 1. Очікуваний KeyCRM payload (спільне для всіх форм)

`POST https://openapi.keycrm.app/v1/pipelines/cards` (у тестах — mock):

| Поле | Значення |
|---|---|
| `title` | `<form_type display> - <name>` |
| `contact.full_name/phone/email` | з форми |
| `source_id` | `resolve_keycrm_source_id()` (UTM/сторінка) |
| `utm_*` | якщо є |
| `custom_fields` | gclid (`KEYCRM_GCLID_FIELD_UUID`), site (`KEYCRM_SITE_FIELD_UUID`), lang (`KEYCRM_LANG_FIELD_UUID`) — лише якщо UUID задані |
| `manager_comment` | рядки `Form: <type>`, **`Site: cz`**, **`Lang: cs\|en`**, `Сторінка заявки: …`, `GCLID: …` |

`lang` визначається: POST `lang` → префікс `/en/` у URL ендпоінта → префікс у Referer → активна мова → `cs`.
`quiz_id`: окремого поля немає; тип квізу видно з `Form: site-request` + `Сторінка заявки:` (`source_page`).
`gclid`: з `GCLIDCapture.appendToFormData` (base.js/home-bundle.js); **tz-generator його не передає**.

---

## 2. Форми

Позначення ендпоінта: CZ = без префікса, EN = `/en/…`.

### 2.1 Головна (`/`, `/en/`)
- Форми: модалка «Nechat poptávku / Get in touch» (`call_request`), футер (`footer-consultation`).
- JS: `home-bundle.js` → **завжди `/forms/submit/` без мовного префікса** (lang береться з Referer).
- Поля: `name`, `phone`, `email`, `telegram`, `message`, `consent` (обов'язково), хоча б один із phone/email/telegram; `gclid`/`utm_*`/`source_page` приховані.
- Успіх CZ: «Děkujeme! Náš manažer vám zavolá do 15 minut.» / footer: «Děkujeme! Brzy se s vámi spojíme.»
- Успіх EN: ⚠ call_request: «Leave your contacts and our manager will call you within 15 minutes» (хибний переклад) / footer: «Thank you! We will contact you soon.»
- ⚠ Оскільки ендпоінт без префікса, EN-користувач на `/en/` отримає **чеські** повідомлення.
- Payload: `Form: call-request|footer-consultation`, `Site: cz`, `Lang: cs|en`, `GCLID` якщо був.

### 2.2 Контакти (`/contacts/`, `/en/contacts/`)
- `data-form-type="contact"`, `base.js` → `localizedFormUrl()`.
- ⚠ **На `main` CZ-сторінки з base.js шлють на `/cs/forms/submit/` → 404** (prefix_default_language=False). Виправлено в `feature/figma-redesign` і `cz/frontend` (`lang === 'cs'` → без префікса), у `main` ще ні.
- Успіх CZ: «Děkujeme za vaši zprávu! Brzy se s vámi spojíme.» EN: «Thank you for your message! We will contact you soon.»
- Payload: `Form: contact`, `Site: cz`, `Lang`.

### 2.3 Internet-shop квіз (`/internet-shop-v2/`, `/en/internet-shop-v2/`)
- `components/internet_shop_v2/brief.html`, `form_type=site_request`, поля квізу `q_need/q_products/q_features/q_start/q_timeline` → JS збирає в `details` (укр. мітки, див. п.12), + lead-поля.
- Успіх CZ: «Děkujeme! Vaše poptávka byla přijata. Brzy se s vámi spojíme.» EN: «Our manager will contact you soon».
- Payload: `Form: site-request`, `Сторінка заявки: /internet-shop-v2/`, `Site: cz`, `Lang`.

### 2.4 Corporate квіз (`/corporate-website-v2/`, `/en/corporate-website-v2/`)
- `components/corporate_website_v2/brief.html` (`site_request`) + «free analysis» (`call_request`).
- Повідомлення — як 2.3 / 2.1. Payload: `Form: site-request|call-request`, `source_page=/corporate-website-v2/`.

### 2.5 Калькулятор (`/calculator/`, `/en/calculator/`)
- `POST /forms/test/` (`/en/forms/test/`), `question_1..5`, `alt-services`, `name`, `phone` (обов'язкові), `email` (опц.), `consent`.
- Успіх CZ: «Děkujeme! Brzy se s vámi spojíme.» EN: «Thank you! We will contact you soon.» → `redirect=/thank-you/`.
- Помилки: CZ «Zadejte platné telefonní číslo (minimálně 10 číslic)», EN «Enter a valid phone number (minimum 10 digits)».
- Payload: `Form: test_result`, відповіді `=== ВІДПОВІДІ НА ТЕСТ ===` (укр.), `Site`, `Lang`.

### 2.6 Генератор ТЗ (`/tz-dlia-saitu/`, `/en/tz-dlia-saitu/`)
- `POST /forms/tz/` (`data-tz-submit` = `{% url 'tz_submit' %}`), поля `name`, `phone`, `email` (усі обов'язкові), `quiz` (JSON). Далі `GET /forms/tz/<token>/pdf/`, `POST /forms/tz/<token>/upsell/`.
- ⚠ Немає `consent` і `gclid/utm` у запиті.
- ⚠ Успіх CZ віддається **українською** («Базове ТЗ готове…»); EN: «Basic brief is ready. Download the PDF — …».
- ⚠ PDF: `build_tz_context()` має лише мітки uk/en/ru → для `cs` PDF **українською** (видно клієнту).
- ⚠ upsell повторно викликає `sync_submission_to_keycrm` → можлива друга картка в KeyCRM.
- Payload: `Form: tz_generator`, `Site: cz`, `Lang`.

### 2.7 Telegram-бот (`/telegram-bot/`, `/en/telegram-bot/`)
- `form_type=telegram-bot`, `bot_task`, `integrations`, `details`, `honeypot` (заповнений → «тихий» успіх без збереження).
- ⚠ Успіх і CZ, і EN — **українською** («Дякуємо! Заявку на Telegram-бота отримано…»; немає перекладу в .po).
- Payload: `Form: telegram-bot`, `Site`, `Lang`.

### 2.8 «Nezávazná poptávka» (`/web-development/`, `/en/web-development/`)
- Кнопка в `components/web_development/calc.html` → модалка `call-request-modal` → `call_request` (як 2.1, але через base.js → див. 404 у 2.2).
- Payload: `Form: call-request`, `Site`, `Lang`.

### Спільні помилки валідації (lead-форми)
| Кейс | HTTP | CZ | EN |
|---|---|---|---|
| без consent | 400 | Potvrďte souhlas se zpracováním osobních údajů. | ⚠ «I agree to the processing of personal data according to» (хибний переклад) |
| невалідний e-mail | 400 | Zadejte platný e-mail. | Enter a valid email |
| ні телефону, ні e-mail, ні Telegram | 400 | Zadejte telefon, e-mail nebo Telegram. | Enter a phone number, email, or Telegram. |
| невалідний Telegram | 400 | Zadejte platný Telegram (@username). | Enter a valid Telegram (@username). |

### Спільне
- Усі успіхи редіректять на `/thank-you/` **без мовного префікса** → EN-користувач потрапляє на CZ thank-you.

---

## 3. Чекліст ручного прогону (runserver, KeyCRM вимкнено)
Для кожної з 8 форм × {CZ, EN}:
1. Відкрити сторінку, заповнити `TEST <форма> <мова>`, `test@example.com`, `+420 777 123 456`, consent.
2. DevTools → Network: URL ендпоінта (немає 404 на `/cs/…`), статус 200, JSON `success: true`, текст мовою сторінки.
3. Негативні кейси: без consent, невалідний e-mail → 400 + текст мовою сторінки.
4. Admin → Form submissions: запис є, `extra_data.site == "cz"`, `extra_data.lang` відповідає сторінці.
5. KeyCRM-payload: у shell із замоканим `requests.post` — `manager_comment` містить `Site: cz` / `Lang: …`.
6. Редірект на thank-you правильною мовою (зараз — ні, див. вище).

## 4. Результат локального smoke (Django test client, 2026-10-19)
22 запити (8 форм + 3 негативні × CZ/EN): усі ендпоінти 200/400 як очікувано, у payload
`Site: cz` і правильний `Lang`. Знайдені проблеми позначено ⚠ вище; `/cs/forms/submit/` → 404.
