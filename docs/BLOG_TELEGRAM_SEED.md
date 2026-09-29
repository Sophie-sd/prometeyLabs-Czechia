# Blog + Telegram bots (PrometeyLabs Czechia)

CS + EN only (no UK/RU public). Source catalogue came from Renova; Czechia
keeps deploy-safe seeds and the `/telegram-bot/` service page.

## Blog

| Piece | Location |
|-------|----------|
| Slugs / dates / categories | `apps/blog/blog_seed_meta.py` |
| Czech copy | `apps/blog/data/blog_i18n_cs.json` |
| English copy | `apps/blog/data/blog_i18n_en.json` |
| Command | `python manage.py seed_initial_data` |

Primary DB fields (`title`, `excerpt`, `content`, `keywords`, SEO) = **Czech**.
English goes into `*_en`. Russian fields are cleared on seed. **15** posts.

```bash
python manage.py seed_initial_data
python manage.py seed_initial_data --prune   # drop rows not in seed catalogue
```

`build.sh` already runs `seed_initial_data` after migrate.

## Telegram bots page

| Piece | Location |
|-------|----------|
| URL | `/telegram-bot/` and `/en/telegram-bot/` |
| View | `TelegramBotView` in `apps/core/views.py` |
| Template | `templates/pages/telegram-bot.html` (hreflang cs+en) |
| CSS (as shipped from Renova) | `static/css/telegram-bot.css` |
| Form type | `telegram-bot` (`0030_formsubmission_telegram_bot`) |

No Render service changes in this pass.

## Local smoke

```bash
python manage.py migrate
python manage.py seed_initial_data --prune
python manage.py runserver 0.0.0.0:8000
# /blog/ /en/blog/ /telegram-bot/ /en/telegram-bot/ → 200
```
