#!/usr/bin/env bash
set -o errexit

echo "🖼️  Ensuring portfolio media files on disk..."
python manage.py seed_portfolio_projects --prune

echo "👥 Ensuring homepage client logos on disk..."
python manage.py seed_clients

echo "📍 Ensuring site contact settings (address/map)..."
python manage.py seed_site_contact_settings

echo "🚀 Starting application..."
# WEB_CONCURRENCY from Render env (starter 512MB → prefer 2). Default 2 if unset.
exec gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker -w "${WEB_CONCURRENCY:-2}"
