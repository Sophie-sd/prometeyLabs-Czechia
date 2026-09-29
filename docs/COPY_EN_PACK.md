# COPY EN PACK — PrometeyLabs Czechia

Agency English pass for the Czechia market fork. Source meaning = Ukrainian `msgid`. Czech `msgstr` used as a hint only (CS also has bad fuzzies). Design / CSS / HTML / `locale/cs` were **not** edited.

**Date:** 2026-09-29 (Europe/Kiev)  
**Repo:** `/Users/sofiadmitrenko/Sites/prometeyLabs-Czechia`  
**No git commit** — working tree left dirty for executor merge.

---

## Summary counts

| Metric | Before (baseline) | After |
|--------|-------------------|-------|
| Empty EN `msgstr` (excl. header) | ~458 | **0** |
| Fuzzy EN entries | ~495–498 | **0** |
| Wrong fuzzy leftovers corrected (consent / images / stock / CTAs / Close Menu, etc.) | — | **~50+** targeted fixes |
| Czechia-aware public string upgrades | — | **~10** (Shoptet/Heureka, Twisto/Comgate, Zásilkovna, Czech law, +420 placeholders in EN defaults) |
| `msgfmt -c` | — | **OK** (added `Plural-Forms: nplurals=2; plural=(n != 1);` to EN header) |

Baseline ≈ state of `locale/en/LC_MESSAGES/django.po` at start of this copy pack (many empties + fuzzies with wrong msgmerge matches). Empties were filled with natural agency EN; all `fuzzy` flags removed once `msgstr` was verified/corrected.

---

## Voice notes

- **Tone:** B2B digital-agency English for Czechia (PrometeyLabs Czechia). Clear, confident, no UA/RU calques.
- **Prefer:** *Get in touch* / *Request a quote* / *Get a site like this* over *Leave a request* / *I want a site like this*.
- **Mobile:** *mobile-friendly* / *reads well on mobile* — never *easy on the phone* / *comfortable on the phone*.
- **Local market (where demos already CZ):** Kč, Czechia, Shoptet/Heureka, Twisto, Comgate/GoPay, Zásilkovna, Czech law + GDPR.
- **Contacts in EN demo defaults:** Prague / Czechia + `+420 777 000 000` + `info@prometeylabs.com` where the string was clearly a demo placeholder (Kyiv / +38). Do **not** invent legal company facts beyond that.
- **Brand names** unchanged (PrometeyLabs, product/portfolio brands).
- **Placeholders** preserved: `%(name)s`, `{n}`, `%d`, `%s`, HTML tags, `&amp;`.
- **Spelling:** British-leaning agency EN (*catalogue*, *localisation*) for consistency with Czechia/EU positioning.
- **Admin/back-office:** still correct EN (managers use EN locale) — including CRM, invoices, subscriptions, GDPR checkboxes.

### Known bad fuzzy patterns that were fixed

| Wrong EN (msgmerge leftover) | Correct EN (examples) |
|------------------------------|------------------------|
| `Website Development Request` on «Згода на обробку даних» | Consent to data processing |
| `online events` on card/story images | Card image (desktop/mobile), Homepage image (stories) |
| `Leave a request` / `Balance` on «Залишок» | Stock / Decrease stock / Increase stock |
| `Close Menu` on unrelated admin UI | Modal / Save and download PDF / Open product card / etc. |
| `Useful Information` on contact/system/extra fields | Contact / System / Additional information |
| `I want a site like this` | Get a site like this |
| `Statistic: easy on the phone` | Statistic: mobile-friendly |

---

## Top public CTAs — before → after (samples)

| # | msgid (UA) | Before (bad / calqued / empty) | After |
|---|------------|--------------------------------|-------|
| 1 | Хочу такий сайт | I want a site like this | **Get a site like this** |
| 2 | Залишити заявку | Leave a request | **Get in touch** |
| 3 | Надіслати заявку | Leave a request / Send request | **Send enquiry** |
| 4 | Отримати розрахунок → | Get a quote (arrow missing) | **Get a quote →** |
| 5 | Отримати консультацію | (various) | **Request a consultation** |
| 6 | Розрахувати вартість | Calculate Cost | **Get a cost estimate** |
| 7 | Замовити дзвінок | Request a Call | **Request a call** |
| 8 | Детальніше | Details | **Learn more** |
| 9 | ОТРИМАТИ РОЗРАХУНОК | GET ESTIMATE | **GET A QUOTE** |
| 10 | Статистика: зручно з телефону | Statistic: easy on the phone | **Statistic: mobile-friendly** |
| 11 | Згода на обробку даних | Website Development Request | **Consent to data processing** |
| 12 | Переросли Prom та OLX? | Outgrown the marketplaces? | **Outgrown Shoptet and Heureka?** |
| 13 | Українська локалізація з коробки | Localisation ready out of the box | **Czech localisation out of the box** |
| 14 | Покупка частинами monobank | Pay in instalments | **Buy now, pay later (Twisto)** |
| 15 | Замовити | Request a Call | **Order** |

Demo CMS CTAs (block defaults):

| Location | Before | After |
|----------|--------|-------|
| democorp hero CTA | (already OK) Get a site like this | unchanged |
| democorp KPI mobile | comfortable on mobile | **mobile-friendly** |
| demolanding hero CTA | Get a landing like this | unchanged |
| demolanding SEO line | …a fast page on the phone | **…mobile-friendly and fast** |
| demoshop hero CTA | View catalog | **View catalogue** |

---

## Open questions

1. **Currency / tax IDs in admin invoice strings** — some UA msgids still say UAH / РНОКПП / ЄДРПОУ. EN now uses neutral “base currency” / “Tax ID / Company ID (IČO)” where filled empty. Confirm whether backend invoice math is still UAH or already CZK before tightening copy further.
2. **`default` vs `default_en` phones** — EN demo contacts moved to `+420 777 000 000` / Prague; Czech `default` / `default_cs` still show legacy `+38` in demolanding/democorp. Intentional (CS pack separate)? Or should CS defaults also move to +420 in a later pass?
3. **Language-switch banner** — UA msgid offers RU→UK switch. EN msgstr adapted to a generic “You’re viewing in Russian — switch to English?”; product may want this string hidden for Czechia EN or rewritten for CS↔EN only.
4. **«Максимальна (UA + світ)»** → “Maximum (Czechia + worldwide)” — confirm product meaning of the UA/world package tier for Czechia pricing pages.
5. **Portfolio case studies** — kept Ukraine-specific delivery/facts (real client work). Only spelling polish (`catalogue`). OK?

---

## Path list for executor merge

```
locale/en/LC_MESSAGES/django.po          # filled + unfuzzied + wrong-match fixes + Plural-Forms header
locale/en/LC_MESSAGES/django.mo          # rebuilt via msgfmt -c (gitignored *.mo — rebuild on deploy)
apps/democorp/block_defaults.py          # default_en polish; Prague/+420 placeholders; mobile-friendly
apps/demoshop/block_defaults.py          # light EN polish (catalogue, voice)
apps/demolanding/block_defaults.py       # default_en polish; Prague/+420; enquiry wording
apps/core/portfolio_i18n_en.py           # light pass (catalogue spelling, minor voice)
docs/COPY_EN_PACK.md                     # this file
```

**Do not merge / did not touch:**

```
locale/cs/**                             # read-only hint
templates/**, static/**, CSS/HTML        # structure untouched
```

### Rebuild `.mo` (if needed on another machine)

```bash
msgfmt -c -o locale/en/LC_MESSAGES/django.mo locale/en/LC_MESSAGES/django.po
```

---

## Success criteria checklist

- [x] `locale/en`: 0 empty `msgstr` (except header `msgid ""`); 0 fuzzy
- [x] block_defaults EN reads as natural agency English; Czechia-aware where demos already CZ
- [x] `docs/COPY_EN_PACK.md` present
- [x] No git commit / push

## Follow-up (Copy, same day)

Spot-fixed leftover bad matches after first pass: `Критично`→Critical, `Відкрити`→Open, Classification / Manager work / Normal / Form type / language-labelled Content & Keywords, budget bands € formatting. Wrapped corporate/shop page title+description+og in `{% trans %}` and added Czechia-ready EN msgstr for those SEO strings.
