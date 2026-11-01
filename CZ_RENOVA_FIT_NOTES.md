# Czech ↔ Renova fit — remaining gaps

Canon: `~/FromAir/prometeyRenova` (read-only). This file lists what was **not** made 1:1, on purpose or still open.

## Kept Czech-only (do not port)

- Languages: `cs` default (unprefixed) + `en` (`/en/`). No RU, no Ukrainian on public pages.
- `TIME_ZONE=Europe/Prague`, `CANONICAL_BASE=https://prometeylabs.cz`
- Legal pages offer/privacy/refund/cookies/IP in cs/en
- First-party GDPR banner + `ConsentLog`
- KeyCRM CZ funnel/source
- CZK (`web_development.WEB_DEV_TIERS` + `eur_to_czk_rounded`)
- `AdminLocaleMiddleware`
- Short URLs without `-v2`; 301 from `/internet-shop-v2/`, `/corporate-website-v2/`
- Payment methods / payment texts in admin
- Bank transfer on payment links; Monobank models/migrations kept, public acquiring off

## Done in this fit

- Header/burger: flat menu Home → Corporate → Shop → Telegram → Dorobka → Portfolio → Blog → Calculator → Contacts. No “Web applications”.
- Removed `web_development` / `web_applications` views, templates, sitemap entries; 301 `/web-development/`, `/webove-aplikace/`, `/web-applications/` (+ `/en/`) → home.
- Home: `service_modals`, no `why_diagrams`, `calc_cta`
- Shop: `cases` / `dropshipping` / `scope`; corp ads FAQ/JSON-LD
- Ads LPs: `/uprava-webu/` ↔ `/en/website-improvement/`, `/tvorba-webu/` ↔ `/en/website-development/`
- `calc_cta` on the same surfaces as Renova (home, shop, corp, ads)
- Admin sidebar “Subscriptions” (`?is_subscription=1`)
- `NoIndexPrivatePathsMiddleware`, `/llms.txt`
- Demo checkout: static Packeta / PPL / Česká pošta / osobní odběr (np_* columns reused, no UA HTTP)
- Democorp: `carousel_nav.html`, `lang.html` (cs/en via existing switcher)

## Gaps

1. **Desktop nav density.** Nine flat items wrap on <1440px. Renova still uses a “Services” dropdown. Czech follows the explicit menu list, not Renova’s dropdown.
2. **Democorp layout ≠ Renova Figma home.** Czech democorp keeps the older carousel (`data-cf`). `carousel_nav` is wired onto that carousel (with `data-cf-prev/next`); Renova `dc-demo` CSS/markup and `next.svg`/`prev.svg` were not copied.
3. **Monobank leftovers (not public UI).** Webhook URL, `monobank_service.get_invoice_status` / pubkey verify, subscription models, `use_acquiring` column remain. Public create-invoice / wallet charge return `None`. Payment page must not show Monobank (existing tests).
4. **Nova Poshta module name.** `apps/demoshop/services/novaposhta.py` is a CZ city fixture (no HTTP). Checkout no longer calls it. JSON endpoints `/api/np/cities/` and `/warehouses/` still exist for old JS; they return CZ fixture data only.
5. **ShopOrder.DeliveryMethod** still `np_warehouse` / `address`. Carrier code is stored in `np_warehouse_ref`. No new migration.
6. **Unused v1 templates** `pages/internet-shop.html`, `internet-shop-ru.html`, `corporate-website.html` are not routed; some still contain Ukrainian/Russian. Do not expose.
7. **Meta/copy still gettext-Ukrainian msgid** on several views (Contacts “Київ, Україна”, legal titles). Public HTML is Czech/English via `.po`; if a string is missing from `locale/cs`, it can leak. Run `compilemessages` after new `{% trans %}`.
8. **`locale/uk` and `locale/ru` directories** may still exist in the repo. They are not in `LANGUAGES`. Do not add them to public `hreflang`.
9. **Currency switcher (EUR/CZK) on removed web-development page** is gone with that page. Calculator still shows Kč orientation. No public fx switcher.
10. **Prices** follow Czech `WEB_DEV_TIERS` (landing 10k–17k Kč, etc.), not Renova €250/500/800 cards.
11. **Pre-existing `static/images/*.png` deletions** in the working tree were left untouched.
12. **`base.html` mobile FAB** still has a pre-existing `!important` rule; not introduced by this fit.
13. **Blog category slug `web-development`** is taxonomy, not the removed page. Keep.
14. **WhatsApp** on Czech home hero was kept (Czech market). Renova may differ.
15. **Full pixel 1:1 of every shop/corp inner block** vs Renova Figma was not re-audited line-by-line after copy; ads FAQ/contacts/process and cases/dropshipping/scope are the structural port.
