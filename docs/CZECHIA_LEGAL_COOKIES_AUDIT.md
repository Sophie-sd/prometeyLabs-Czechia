# Czechia — legal / cookies / GDPR audit

**Date:** 2026-09-29 (EEST)  
**Source (copy):** `~/prometeyRenova — копия`  
**Target:** `~/Sites/prometeyLabs-Czechia`  
**Scope:** company/tax/address/emails, privacy/terms/cookies pages, CookieYes prep, GDPR-related env. No deploy.

## Summary

Legal **page templates** and **CookieYes code path** already match the Renova copy. Main Czechia **code** gaps vs UA stack are intentional (cs/en, Prague TZ, separate Render service). The real **data** gap was empty impressum i18n fields in local sqlite (filled from copy this session; **not** in git — `db.sqlite3` is ignored). **Prod** still needs CookieYes Site ID + mail/host env; entity remains UA OSVČ/ФОП (same as copy), not a Czech s.r.o.

## Settings (company, tax, address, emails)

| Item | Czechia repo | vs copy | Notes |
|------|--------------|---------|--------|
| `LANGUAGE_CODE` / `LANGUAGES` | `cs`; `cs`+`en` | Copy: `uk` + uk/en/ru/cs | Intentional Czechia fork |
| `TIME_ZONE` | `Europe/Prague` | Copy: `Europe/Kyiv` | OK |
| Unfold admin title | PrometeyLabs Czechia | Copy: PrometeyLabs | OK |
| `CONTACT_EMAIL` / `DEFAULT_FROM_EMAIL` defaults | `info@prometeylabs.com` | Same | Render slots `sync: false` — set Czechia mailboxes on deploy |
| `SiteContactSettings` legal entity | ФОП Дмитренко… / РНОКПП `3770706565` | Same base fields | privacy-cs already cites this as OSVČ + Czech tax/accountancy refs |
| `legal_name_cs` / `address_cs` / `legal_address_*` | Were **empty** in Czechia sqlite | Copy has CS/EN/RU filled | **Fixed locally** from copy (see below). Re-apply in **prod admin** or seed after migrate |
| Phone / maps | UA `+38…`, Kyiv address | Same as copy | Business decision if CZ phone/address needed |

### Impressum values restored from copy (local DB only)

```
legal_name_cs      = Sofiia Dmytrenko, OSVČ
legal_name_en      = Sofiia Dmytrenko, Private Entrepreneur
legal_name_ru      = ФЛП Дмитренко София Дмитриевна
address_cs         = bulvár Tarase Ševčenka 46a, Kyjev
address_en         = 46a Taras Shevchenko Blvd, Kyiv
address_ru         = Киев, бульвар Тараса Шевченко 46а
legal_address_cs   = ul. Kvaši, d. 2, Myrhorod, Poltavská obl.
legal_address_en   = 2 Kvashi St, Myrhorod, Poltava Region
legal_address_ru   = Полтавская обл., г. Миргород, ул. Кваши, дом 2
```

No new Czech IČO/DIČ in either tree — still Ukrainian registration number.

## Legal docs (privacy / terms / cookies / offer / IP / refund)

| Page | Status |
|------|--------|
| `privacy.html` + `-cs/-en/-ru` | **Same** as copy; `privacy-cs` body is CZ/GDPR/ÚOOÚ-oriented |
| `cookies.html` + locales | **Same**; cookies-cs cites §89 ZEKom, ÚOOÚ Praha |
| `offer*.html`, `intellectual-property*.html`, `refund*.html` | **Same** as copy |
| Routes | `/privacy/`, `/cookies/` (+ offer/refund/IP via core views) present |
| Residual | `{% block title/description %}` on `*-cs.html` still use Ukrainian `{% trans %}` strings (same in copy) — body Czech OK |
| `newpoliticdoc/` DOCX | UA source docs present in both; site uses HTML templates |

Footer impressum + CookieYes revisit (`cky-banner-element`) present (same pattern as copy).

## CookieYes / banner prep

| Piece | Status |
|-------|--------|
| `COOKIEYES_ID` in `settings.py` + context processor | Present (same as copy) |
| `.env.example` `COOKIEYES_ID=` | Present |
| `render.yaml` `COOKIEYES_ID` `sync: false` | Present |
| `templates/partials/gtm_head.html` Consent Mode → deferred CookieYes → GTM | **Same** as copy |
| CSP allow `cdn-cookieyes.com` | Present (`apps/core/middleware.py`) |
| Tests `test_cookieyes_defer.py` | Present |
| Local `.env` | **No** `COOKIEYES_ID` key (banner off locally — expected) |
| Prod | **Checklist open:** set Site ID in Render; CookieYes dashboard (GCM/GDPR/365/langs); see `docs/CZ_EU_COMPLIANCE_CHECKLIST.md` |

## GDPR-related env / forms

| Item | Status |
|------|--------|
| Lead GDPR partial `lead_gdpr_min.html` | Present (same as copy; consent strings still UA source for gettext) |
| Checkout consents `_checkout_consents.html` | Present |
| `data_protection_email` | `info@prometeylabs.com` (both) |
| `.env.example` `LANGUAGE_CODE=uk` | **Stale comment/value** vs hardcoded `cs` in `config/settings.py` — cosmetic; settings does not read `LANGUAGE_CODE` from env |
| Render `LANGUAGE_CODE=cs` | Set in blueprint |

## What was fixed this session

1. **Local sqlite only:** filled empty `SiteContactSettings` `*_cs/*_en/*_ru` from Renova copy (gitignored — **not pushed**).
2. **This audit file** committed under `docs/`.

**Not done (by design):** no deploy; no CookieYes Site ID invent; no new Czech company/IČO; no migration (avoids clash with untracked local `0030_*` WIP); no rewrite of legal HTML (already = copy).

## Prod checklist (manual)

1. Admin → Site contact: paste impressum i18n values above (or re-import from Renova DB).
2. Render: `COOKIEYES_ID`, `CONTACT_EMAIL` / `DEFAULT_FROM_EMAIL`, hosts/`SITE_URL` (see `docs/RENDER_CZECHIA.md`).
3. CookieYes dashboard + GTM Consent Mode E2E (checklist §2 / prod runbook).
4. Decide whether UA OSVČ impressum is enough for CZ audience or a CZ entity is required (business/legal).
