# Portfolio seed (PrometeyLabs Czechia)

Idempotent portfolio load for the Czechia fork (`LANGUAGE_CODE=cs`, public
locales **cs** + **en** only). Source catalogue lives in Renova
(`prometeyRenova`); this repo keeps the same seed modules with CS/EN copy.

## What gets seeded

| Piece | Location |
|-------|----------|
| Project rows | `apps/core/portfolio_seed_projects_{1,2,3}.py` → `PORTFOLIO_PROJECTS` |
| Czech + English text | `apps/core/portfolio_i18n_cs.py`, `portfolio_i18n_en.py` |
| Card screens (git) | `static/images/portfolio/screens/<slug>-desktop.webp` / `-mobile.webp` |
| Runtime media copies | `media/portfolio/<slug>/` (disk / Render persistent disk) |

Primary DB fields (`title`, `subtitle`, `card_description`, `integrations`,
`card_image_alt`) are filled with **Czech**. English goes into `*_en`.
Ukrainian/Russian public fields are cleared on seed.

~55 projects in seed; ~47 have `show_on_portfolio=True`. Homepage client logos
are seeded separately by `seed_clients` (see `HOME_CLIENTS`).

## Commands

```bash
# Full idempotent upsert + copy missing images from static → media
python manage.py seed_portfolio_projects

# Also delete rows not in PORTFOLIO_PROJECTS (used on Render start)
python manage.py seed_portfolio_projects --prune

# Re-copy images even when media files already exist
python manage.py seed_portfolio_projects --prune --force-images
```

Images are resolved **static-first** (`apps/core/portfolio_images.py`), so
collectstatic alone is enough for cards if the media disk is empty; seed still
copies into `MEDIA_ROOT` for admin / disk-backed URLs.

## How it runs on Render

1. **Build** (`./build.sh`): after `migrate`, runs  
   `python manage.py seed_portfolio_projects --prune --force-images`  
   (plus `seed_clients` and other seeds).
2. **Start** (`./scripts/start.sh`): runs  
   `python manage.py seed_portfolio_projects --prune`  
   then `seed_clients`, then gunicorn.  
   This re-applies rows and ensures media files exist on the attached disk
   (`prometeylabs-czechia-media`) after every restart without wiping custom
   admin edits to non-seed fields beyond the seeded defaults.

No separate fixture JSON is required. Do **not** commit `media/` (gitignored);
ship screens under `static/images/portfolio/`.

## Local smoke

```bash
python manage.py migrate
python manage.py seed_portfolio_projects --prune --force-images
python manage.py runserver 0.0.0.0:8000
# CS (default):  http://127.0.0.1:8000/portfolio/     → 200, project cards
# EN:            http://127.0.0.1:8000/en/portfolio/  → 200, English copy
```

## Regenerating screenshots

```bash
python manage.py capture_portfolio_screens   # Playwright → static/images/portfolio/screens/
python manage.py seed_portfolio_projects --force-images
```

## Related docs

- `docs/RENDER_CZECHIA.md` — new Render service / disk / env
- `docs/COPY_EN_PACK.md` — EN gettext polish notes
