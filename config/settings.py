from pathlib import Path
import os
from dotenv import load_dotenv
from django.urls import reverse_lazy
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-CHANGE-IN-PRODUCTION')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# ALLOWED_HOSTS
ALLOWED_HOSTS = [h.strip() for h in os.environ.get('ALLOWED_HOSTS', '').split(',') if h.strip()]

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.extend([RENDER_EXTERNAL_HOSTNAME, f'www.{RENDER_EXTERNAL_HOSTNAME}'])

if DEBUG:
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1', '0.0.0.0', '127.0.0.1:8000', 'localhost:8000', 'testserver', '*'])

# APPS
INSTALLED_APPS = [
    # Unfold — ЗАВЖДИ перед django.contrib.admin
    "unfold",
    "unfold.contrib.filters",

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',

    'tinymce',

    'apps.core',
    'apps.blog',
    'apps.payment',
    'apps.demotenant',
    'apps.demoshop',
    'apps.demolanding',
    'apps.democorp',
]

# UNFOLD ADMIN
UNFOLD = {
    "SITE_TITLE": "PrometeyLabs Czechia",
    "SITE_HEADER": _("PrometeyLabs Czechia — Administrace"),
    "SITE_URL": "apps.demotenant.admin_site_url.resolve_view_site_url",
    "SITE_ICON": lambda request: static("images/favicon-48x48.png"),
    "SITE_LOGO": {
        "light": lambda request: static("images/favicon-48x48.png"),
        "dark": lambda request: static("images/favicon-48x48.png"),
    },
    "SITE_FAVICONS": [
        {"rel": "icon", "sizes": "16x16", "type": "image/png",
         "href": lambda request: static("images/favicon-16x16.png")},
        {"rel": "icon", "sizes": "32x32", "type": "image/png",
         "href": lambda request: static("images/favicon-32x32.png")},
        {"rel": "icon", "sizes": "48x48", "type": "image/png",
         "href": lambda request: static("images/favicon-48x48.png")},
    ],
    "COLORS": {
        "primary": {
            "50":  "255 247 237",
            "100": "255 237 213",
            "200": "254 215 170",
            "300": "253 186 116",
            "400": "251 146 60",
            "500": "249 115 22",
            "600": "234 88 12",
            "700": "194 65 12",
            "800": "154 52 18",
            "900": "124 45 18",
            "950": "67 20 7",
        },
    },
    "STYLES": [
        lambda request: static("admin/css/admin-primary-buttons.css"),
        lambda request: static("admin/css/admin-list-filters.css"),
        lambda request: static("admin/css/admin-sidebar-logo.css"),
        lambda request: static("admin/css/admin-image-preview.css"),
        lambda request: static("demotenant/css/admin_changelist_mobile.css"),
        lambda request: static("demoshop/css/demoshop_admin.css"),
    ],
    "SCRIPTS": [
        lambda request: static("admin/js/admin-list-filters.js"),
    ],
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": _("CRM — Poptávky"),
                "items": [
                    {
                        "title": _("Poptávky"), "icon": "inbox", "link": reverse_lazy("admin:core_formsubmission_changelist"),
                        "permission": "apps.demoshop.admin_permissions.is_prometey_staff",
                    },
                ],
            },
            {
                "title": _("Platby"),
                "separator": True,
                "items": [
                    {"title": _("Odkazy"),     "icon": "link",            "link": reverse_lazy("admin:payment_paymentlink_changelist"), "permission": "apps.demoshop.admin_permissions.is_prometey_staff"},
                    {"title": _("Předplatné"),      "icon": "autorenew",       "link": "/admin/payment/paymentlink/?is_subscription=1", "permission": "apps.demoshop.admin_permissions.is_prometey_staff"},
                    {"title": _("Faktury"),       "icon": "receipt_long",    "link": reverse_lazy("admin:payment_invoice_changelist"), "permission": "apps.demoshop.admin_permissions.is_prometey_staff"},
                    {"title": _("Příjemci"),   "icon": "account_balance", "link": reverse_lazy("admin:payment_recipientprofile_changelist"), "permission": "apps.demoshop.admin_permissions.is_prometey_staff"},
                    {"title": _("Nastavení"), "icon": "settings",        "link": reverse_lazy("admin:payment_paymentsettings_changelist"), "permission": "apps.demoshop.admin_permissions.is_prometey_staff"},
                ],
            },
            {
                "title": _("Web"),
                "separator": True,
                "items": [
                    {
                        "title": _("Kontakty a mapa"),
                        "icon": "contact_phone",
                        "link": reverse_lazy("admin:core_sitecontactsettings_changelist"),
                        "permission": "apps.demoshop.admin_permissions.is_prometey_staff",
                    },
                    {
                        "title": _("Klienti"),
                        "icon": "groups",
                        "link": reverse_lazy("admin:core_client_changelist"),
                        "permission": "apps.demoshop.admin_permissions.is_prometey_staff",
                    },
                    {
                        "title": _("Portfolio"),
                        "icon": "work",
                        "link": reverse_lazy("admin:core_portfolioproject_changelist"),
                        "permission": "apps.demoshop.admin_permissions.is_prometey_staff",
                    },
                    {
                        "title": _("Obchodní nabídky"),
                        "icon": "description",
                        "link": reverse_lazy("admin:core_proposal_changelist"),
                        "permission": "apps.demoshop.admin_permissions.is_prometey_staff",
                    },
                ],
            },
            {
                "title": _("Blog"),
                "separator": True,
                "items": [
                    {
                        "title": _("Články"), "icon": "article", "link": reverse_lazy("admin:blog_blogpost_changelist"),
                        "permission": "apps.demoshop.admin_permissions.is_prometey_staff",
                    },
                ],
            },
            {
                "title": _("Demo weby"),
                "separator": True,
                "items": [
                    {
                        "title": _("Obchody"),
                        "icon": "storefront",
                        "link": reverse_lazy("admin:demoshop_demoshop_changelist"),
                        "permission": "apps.demoshop.admin_permissions.is_prometey_staff",
                    },
                    {
                        "title": _("Firemní weby"),
                        "icon": "domain",
                        "link": reverse_lazy("admin:democorp_corpsite_changelist"),
                        "permission": "apps.demoshop.admin_permissions.is_prometey_staff",
                    },
                    {
                        "title": _("Landing pages"),
                        "icon": "web",
                        "link": reverse_lazy("admin:demolanding_landingsite_changelist"),
                        "permission": "apps.demoshop.admin_permissions.is_prometey_staff",
                    },
                ],
            },
            {
                "title": _("Můj obchod"),
                "separator": True,
                "items": [
                    {"title": _("Obsah a barvy"), "icon": "palette", "link": reverse_lazy("admin:demoshop_shopblock_changelist"), "permission": "apps.demoshop.admin_permissions.is_demo_client"},
                    {"title": _("Produkty"), "icon": "inventory_2", "link": reverse_lazy("admin:demoshop_shopproduct_changelist"), "permission": "apps.demoshop.admin_permissions.is_demo_client"},
                    {"title": _("Kategorie"), "icon": "category", "link": reverse_lazy("admin:demoshop_shopcategory_changelist"), "permission": "apps.demoshop.admin_permissions.is_demo_client"},
                    {"title": _("Recenze"), "icon": "star", "link": reverse_lazy("admin:demoshop_shopreview_changelist"), "permission": "apps.demoshop.admin_permissions.is_demo_client"},
                    {"title": _("Objednávky"), "icon": "receipt_long", "link": reverse_lazy("admin:demoshop_shoporder_changelist"), "permission": "apps.demoshop.admin_permissions.is_demo_client"},
                ],
            },
            {
                "title": _("Můj web"),
                "separator": True,
                "items": [
                    {"title": _("Obsah a styl"), "icon": "palette", "link": reverse_lazy("admin:democorp_corpblock_changelist"), "permission": "apps.demotenant.permissions.is_demo_corp_client"},
                    {"title": _("Fáze práce"), "icon": "precision_manufacturing", "link": reverse_lazy("admin:democorp_corpproductionstep_changelist"), "permission": "apps.demotenant.permissions.is_demo_corp_client"},
                    {"title": _("Galerie"), "icon": "photo_library", "link": reverse_lazy("admin:democorp_corpgalleryimage_changelist"), "permission": "apps.demotenant.permissions.is_demo_corp_client"},
                    {"title": _("Kategorie katalogu"), "icon": "category", "link": reverse_lazy("admin:democorp_corpcategory_changelist"), "permission": "apps.demotenant.permissions.is_demo_corp_catalog_client"},
                    {"title": _("Ukázky webů"), "icon": "inventory_2", "link": reverse_lazy("admin:democorp_corpproduct_changelist"), "permission": "apps.demotenant.permissions.is_demo_corp_catalog_client"},
                    {"title": _("Recenze"), "icon": "star", "link": reverse_lazy("admin:democorp_corptestimonial_changelist"), "permission": "apps.demotenant.permissions.is_demo_corp_client"},
                    {"title": _("Partneři"), "icon": "handshake", "link": reverse_lazy("admin:democorp_corppartner_changelist"), "permission": "apps.demotenant.permissions.is_demo_corp_client"},
                    {"title": _("Poptávky"), "icon": "mail", "link": reverse_lazy("admin:democorp_corplead_changelist"), "permission": "apps.demotenant.permissions.is_demo_corp_client"},
                ],
            },
            {
                "title": _("Můj landing"),
                "separator": True,
                "items": [
                    {"title": _("Obsah a styl"), "icon": "palette", "link": reverse_lazy("admin:demolanding_landingblock_changelist"), "permission": "apps.demotenant.permissions.is_demo_landing_client"},
                    {"title": _("Služby"), "icon": "handyman", "link": reverse_lazy("admin:demolanding_landingoffer_changelist"), "permission": "apps.demotenant.permissions.is_demo_landing_client"},
                    {"title": _("Galerie"), "icon": "photo_library", "link": reverse_lazy("admin:demolanding_landinggalleryimage_changelist"), "permission": "apps.demotenant.permissions.is_demo_landing_client"},
                    {"title": _("Před / po"), "icon": "compare", "link": reverse_lazy("admin:demolanding_landingbeforeafter_changelist"), "permission": "apps.demotenant.permissions.is_demo_landing_client"},
                    {"title": _("Recenze"), "icon": "star", "link": reverse_lazy("admin:demolanding_landingtestimonial_changelist"), "permission": "apps.demotenant.permissions.is_demo_landing_client"},
                    {"title": _("Partneři"), "icon": "handshake", "link": reverse_lazy("admin:demolanding_landingpartner_changelist"), "permission": "apps.demotenant.permissions.is_demo_landing_client"},
                    {"title": _("Poptávky"), "icon": "mail", "link": reverse_lazy("admin:demolanding_landinglead_changelist"), "permission": "apps.demotenant.permissions.is_demo_landing_client"},
                ],
            },
            {
                "title": _("Systém"),
                "separator": True,
                "items": [
                    {
                        "title": _("Uživatelé"),
                        "icon": "person",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                        "permission": "apps.core.admin_permissions.can_manage_admin_users",
                    },
                ],
            },
        ],
    },
}

# MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'apps.core.middleware.CSPMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Додаємо no-cache middleware для розробки
if DEBUG:
    MIDDLEWARE.append('prometey_project.middleware.NoCacheMiddleware')

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# DATABASE - PostgreSQL для Render, SQLite для локальної розробки
import dj_database_url

DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Продакшн (Render) - PostgreSQL
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Локальна розробка - SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# INTERNATIONALIZATION — PrometeyLabs Czechia (cs default unprefixed, en → /en/)
LANGUAGE_CODE = 'cs'
LANGUAGES = [
    ('cs', 'Čeština'),
    ('en', 'English'),
]
LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]
TIME_ZONE = 'Europe/Prague'
USE_I18N = True
USE_TZ = True

# STATIC & MEDIA
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = Path(os.environ.get('MEDIA_ROOT', BASE_DIR / 'media'))
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise налаштування
if DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    # Продакшн: WhiteNoise з gzip/brotli компресією CSS/JS під час collectstatic
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
    WHITENOISE_MAX_AGE = 31536000
    WHITENOISE_SKIP_COMPRESS_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'zip', 'gz', 'bz2']
    WHITENOISE_IMMUTABLE_FILE_TEST = lambda path, url: url.startswith('/static/') and ('.' in url)

# TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.csrf',
                'apps.core.context_processors.global_settings',
            ],
        },
    },
]

# EMAIL
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'your-email@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'your-password')
EMAIL_TIMEOUT = 10  # Максимум 10 секунд для email операцій

# MAILGUN
ANYMAIL = {
    "MAILGUN_API_KEY": os.environ.get('MAILGUN_API_KEY', ''),
    "MAILGUN_SENDER_DOMAIN": os.environ.get('MAILGUN_DOMAIN', 'mg.prometeylabs.com'),
}

DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'Prometey Labs <info@prometeylabs.com>')
CONTACT_EMAIL = os.environ.get('CONTACT_EMAIL', 'info@prometeylabs.com')

# MONOBANK - Зберігаємо поточні налаштування
MONOBANK_TOKEN = os.environ.get('MONOBANK_TOKEN', '')
MONOBANK_SUBSCRIPTION_TOKEN = os.environ.get('MONOBANK_SUBSCRIPTION_TOKEN', MONOBANK_TOKEN)
SITE_URL = os.environ.get('SITE_URL', 'http://localhost:8000')
if DEBUG:
    SITE_URL = os.environ.get('SITE_URL', 'http://localhost:8000')

# FACEBOOK PIXEL
FACEBOOK_PIXEL_ID = os.environ.get('FACEBOOK_PIXEL_ID', '1991082531458369')

# CookieYes CMP Site ID (порожньо = банер не рендериться, для local/dev)
COOKIEYES_ID = os.environ.get('COOKIEYES_ID', '')

# KEYCRM
KEYCRM_API_KEY = os.environ.get('KEYCRM_API_KEY', '')
KEYCRM_PIPELINE_ID = int(os.environ.get('KEYCRM_PIPELINE_ID', '1'))
# Загальний fallback source_id для заявок без платних UTM і без лендінгових ознак
# (форми з головної, footer, контактів тощо).
KEYCRM_SOURCE_ID = os.environ.get('KEYCRM_SOURCE_ID', '')
KEYCRM_GCLID_FIELD_UUID = os.environ.get('KEYCRM_GCLID_FIELD_UUID', '')
KEYCRM_WEBHOOK_SECRET = os.environ.get('KEYCRM_WEBHOOK_SECRET', '')
KEYCRM_SUCCESS_STATUS_ID = os.environ.get('KEYCRM_SUCCESS_STATUS_ID', '')

# KEYCRM — розподіл джерел: платний Google Ads vs органіка з лендінгів.
# Числові ID джерел з KeyCRM (Налаштування → Джерела). Якщо ID не задано —
# resolver використає наступний у пріоритеті або загальний KEYCRM_SOURCE_ID.
KEYCRM_SOURCE_INSTAGRAM = os.environ.get('KEYCRM_SOURCE_INSTAGRAM', '')
KEYCRM_SOURCE_PAID_SHOPS = os.environ.get('KEYCRM_SOURCE_PAID_SHOPS', '')
KEYCRM_SOURCE_PAID_CORPORATE = os.environ.get('KEYCRM_SOURCE_PAID_CORPORATE', '')
KEYCRM_SOURCE_PAID_ALL = os.environ.get('KEYCRM_SOURCE_PAID_ALL', '')
KEYCRM_SOURCE_ORGANIC_SHOPS = os.environ.get('KEYCRM_SOURCE_ORGANIC_SHOPS', '')
KEYCRM_SOURCE_ORGANIC_CORPORATE = os.environ.get('KEYCRM_SOURCE_ORGANIC_CORPORATE', '')

# Підрядки для зіставлення utm_source / utm_campaign (через кому, case-insensitive).
# Пріоритет: Instagram (utm_source) → Shops → Corporate → All (utm_campaign).
KEYCRM_UTM_MATCH_INSTAGRAM = os.environ.get('KEYCRM_UTM_MATCH_INSTAGRAM', '')
KEYCRM_UTM_MATCH_PAID_SHOPS = os.environ.get('KEYCRM_UTM_MATCH_PAID_SHOPS', '')
KEYCRM_UTM_MATCH_PAID_CORPORATE = os.environ.get('KEYCRM_UTM_MATCH_PAID_CORPORATE', '')
KEYCRM_UTM_MATCH_PAID_ALL = os.environ.get('KEYCRM_UTM_MATCH_PAID_ALL', '')

# GOOGLE ADS API
GOOGLE_ADS_DEVELOPER_TOKEN = os.environ.get('GOOGLE_ADS_DEVELOPER_TOKEN', '')
GOOGLE_ADS_CLIENT_ID = os.environ.get('GOOGLE_ADS_CLIENT_ID', '')
GOOGLE_ADS_CLIENT_SECRET = os.environ.get('GOOGLE_ADS_CLIENT_SECRET', '')
GOOGLE_ADS_REFRESH_TOKEN = os.environ.get('GOOGLE_ADS_REFRESH_TOKEN', '')
GOOGLE_ADS_CUSTOMER_ID = os.environ.get('GOOGLE_ADS_CUSTOMER_ID', '')
GOOGLE_ADS_LOGIN_CUSTOMER_ID = os.environ.get('GOOGLE_ADS_LOGIN_CUSTOMER_ID', '')
GOOGLE_ADS_CONVERSION_ACTION_ID = os.environ.get('GOOGLE_ADS_CONVERSION_ACTION_ID', '')

# CSRF налаштування - ВИПРАВЛЕНО
# Завжди включаємо основні домени
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()
]
_site_url = os.environ.get('SITE_URL', '').rstrip('/')
if _site_url and _site_url not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append(_site_url)

# Додаємо динамічний RENDER URL якщо є
RENDER_EXTERNAL_URL = os.environ.get('RENDER_EXTERNAL_URL', '').rstrip('/')
if RENDER_EXTERNAL_URL:
    from urllib.parse import urlparse
    parsed = urlparse(RENDER_EXTERNAL_URL)
    origin = f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme and parsed.netloc else RENDER_EXTERNAL_URL
    if origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(origin)
    host = parsed.netloc or origin.replace('https://', '').replace('http://', '')
    if host and host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)

# Для локальної розробки
if DEBUG:
    CSRF_TRUSTED_ORIGINS.extend([
        'http://localhost:8000',
        'http://localhost:8001', 
        'http://127.0.0.1:8000',
        'http://127.0.0.1:8001',
        'http://0.0.0.0:8000'
    ])

# Tag Assistant / GTM Preview відкриває сайт у popup і потребує window.opener.
# Дефолт Django ('same-origin') рве цей зв'язок → «Не удалось подключиться».
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin-allow-popups'

# Security headers (тільки для продакшн)
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False') == 'True'

# LOGGING
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.core.keycrm_service': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.core.google_ads_service': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.core.webhooks': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}

if DEBUG:
    LOGGING['handlers']['file'] = {
        'level': 'INFO',
        'class': 'logging.FileHandler',
        'filename': os.path.join(BASE_DIR, 'debug.log'),
        'formatter': 'verbose',
    }
    for logger in ['django', 'apps']:
        LOGGING['loggers'][logger]['handlers'].append('file')
        LOGGING['loggers'][logger]['level'] = 'DEBUG'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# TinyMCE (редактор контенту блогу в адмінці)
TINYMCE_DEFAULT_CONFIG = {
    'height': 420,
    'language': 'cs',
    'skin': 'oxide-dark',
    'content_css': 'dark',
    'menubar': False,
    'statusbar': True,
    'plugins': 'lists link autoresize code',
    'toolbar': (
        'undo redo | fontfamily fontsize | '
        'bold italic underline | forecolor backcolor | '
        'bullist numlist link | removeformat | code'
    ),
    'font_family_formats': (
        'Arial=arial,helvetica,sans-serif; '
        'Helvetica=helvetica neue,helvetica,arial,sans-serif; '
        'Georgia=georgia,palatino,serif; '
        'Times New Roman=times new roman,times,serif'
    ),
    'fontsize_formats': '12px 14px 16px 18px 20px 24px 32px',
    'content_style': (
        'body { font-family: Arial, Helvetica, sans-serif; font-size: 16px; '
        'color: #f9fafb; background-color: #222f3e; }'
    ),
    'branding': False,
    'promotion': False,
    'relative_urls': False,
}

TINYMCE_EXTRA_MEDIA = {
    'css': {
        'all': ['admin/css/tinymce-admin.css'],
    },
}