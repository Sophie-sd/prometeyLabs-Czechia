# Render — PrometeyLabs Czechia (new service)

This repo deploys as a **new** Render web service. It must **not** reuse
`prometeylabs.com` / the existing `prometei-web` service.

## Blueprint (`render.yaml`)

| Setting | Value |
|--------|--------|
| Service name | `prometeylabs-czechia` |
| Disk name | `prometeylabs-czechia-media` |
| Region | `frankfurt` |
| `LANGUAGE_CODE` | `cs` |
| Runtime | Python 3.12.7 |

`SITE_URL`, `RENDER_EXTERNAL_HOSTNAME`, `ALLOWED_HOSTS`, and
`CSRF_TRUSTED_ORIGINS` are **not** set to `prometeylabs.com`. Fill them in the
dashboard after the first deploy with the onrender hostname.

## Dashboard steps (Render CLI not required)

1. Open [Render Dashboard](https://dashboard.render.com/) → **New** → **Blueprint**.
2. Connect GitHub repo `Sophie-sd/prometeyLabs-Czechia`, branch `main`
   (or merge PR `czechia-cs-en` first).
3. Confirm Blueprint creates service **`prometeylabs-czechia`** with disk
   **`prometeylabs-czechia-media`** (do not select the old `prometei-web` service).
4. After first deploy, open the service → **Settings** / **Environment**:
   - `RENDER_EXTERNAL_HOSTNAME` = `prometeylabs-czechia.onrender.com`
     (use the exact hostname Render shows; **not** `prometeylabs.com`)
   - `SITE_URL` = `https://prometeylabs-czechia.onrender.com`
   - `ALLOWED_HOSTS` = `prometeylabs-czechia.onrender.com`
   - `CSRF_TRUSTED_ORIGINS` = `https://prometeylabs-czechia.onrender.com`
   - Set `DEFAULT_FROM_EMAIL` / `CONTACT_EMAIL` for Czechia mailboxes
   - Attach PostgreSQL (`DATABASE_URL`) if not linked by Blueprint
5. **Manual Deploy** → clear build cache if locales look stale.
6. Optional later: attach a Czechia custom domain and update the four host/URL
   env vars. Keep them distinct from the Ukraine `prometeylabs.com` stack.

## Local check before deploy

```bash
export DJANGO_SETTINGS_MODULE=config.settings
python -c "from django.conf import settings; print(settings.LANGUAGE_CODE, settings.LANGUAGES, settings.TIME_ZONE)"
# expect: cs [('cs', 'Čeština'), ('en', 'English')] Europe/Prague
```

## i18n reminder

- Default language: **Czech** (`cs`) — **no** URL prefix
- English: `/en/...`
- Ukrainian and Russian locales removed from this fork
