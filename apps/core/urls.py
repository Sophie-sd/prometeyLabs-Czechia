from django.urls import path
from django.utils.functional import lazy
from django.utils.translation import get_language
from django.views.generic import RedirectView
from . import proposal_views
from . import tz_views
from . import views
from . import webhooks


def _route_per_language(cs: str, en: str):
    """Lazy route: Czech slug for cs (default, unprefixed), English slug for /en/.

    Same mechanism as gettext_lazy routes (Django caches the compiled pattern per
    active language), but without depending on .mo files.
    """
    def _pick() -> str:
        return en if (get_language() or '').startswith('en') else cs
    return lazy(_pick, str)()

urlpatterns = [
    # Основні сторінки
    path('', views.HomeView.as_view(), name='home'),
    path('portfolio/', views.PortfolioView.as_view(), name='portfolio'),
    path('calculator/', views.CalculatorView.as_view(), name='calculator'),
    path('developer/', views.DeveloperView.as_view(), name='developer'),
    path('contacts/', views.ContactsView.as_view(), name='contacts'),
    path('telegram-bot/', views.TelegramBotView.as_view(), name='telegram_bot'),
    path('offer/', views.OfferView.as_view(), name='offer'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('cookies/', views.CookiesView.as_view(), name='cookies'),
    path('refund/', views.RefundPolicyView.as_view(), name='refund'),
    path('intellectual-property/', views.IntellectualPropertyView.as_view(), name='intellectual_property'),
    # v2-сторінки зайняли канонічні URL; старі v1-view більше не маршрутизуються
    # (шаблони збережено). Імена internet_shop / corporate_website — аліаси.
    path('internet-shop/', views.InternetShopV2View.as_view(), name='internet_shop_v2'),
    path('internet-shop/', views.InternetShopV2View.as_view(), name='internet_shop'),
    path('corporate-website/', views.CorporateWebsiteV2View.as_view(), name='corporate_website_v2'),
    path('corporate-website/', views.CorporateWebsiteV2View.as_view(), name='corporate_website'),
    # 301 зі старих v2-URL (query string зберігається; #anchor браузер переносить сам)
    path('internet-shop-v2/', RedirectView.as_view(pattern_name='internet_shop_v2', permanent=True, query_string=True)),
    path('corporate-website-v2/', RedirectView.as_view(pattern_name='corporate_website_v2', permanent=True, query_string=True)),
    path('web-development/', views.WebDevelopmentView.as_view(), name='web_development'),
    # Webové aplikace: /webove-aplikace/ (cs) · /en/web-applications/ (en).
    # Same name on all three: Django's reverse() prefers the LAST pattern with a given
    # name, so the language-dependent route must stay last. The literal aliases let
    # resolve() / translate_path() accept the other language's slug; the view 301s
    # such requests to the canonical URL.
    path('webove-aplikace/', views.WebApplicationsView.as_view(), name='web_applications'),
    path('web-applications/', views.WebApplicationsView.as_view(), name='web_applications'),
    path(_route_per_language('webove-aplikace/', 'web-applications/'), views.WebApplicationsView.as_view(), name='web_applications'),
    path('tz-dlia-saitu/', tz_views.TzGeneratorView.as_view(), name='tz_generator'),
    path('thank-you/', views.ThankYouView.as_view(), name='thank_you'),
    path(
        'proposal/<slug:slug>/',
        proposal_views.ProposalDetailView.as_view(),
        name='proposal_detail',
    ),

    # AJAX обробка форм
    path('forms/submit/', views.handle_form_submission, name='form_submit'),
    path('forms/test/', views.handle_test_submission, name='test_submit'),
    path('forms/tz/', tz_views.handle_tz_submission, name='tz_submit'),
    path('forms/tz/<str:token>/pdf/', tz_views.download_tz_pdf, name='tz_pdf'),
    path('forms/tz/<str:token>/upsell/', tz_views.handle_tz_upsell, name='tz_upsell'),

    # Webhooks
    path('webhook/keycrm/', webhooks.keycrm_webhook, name='keycrm_webhook'),
]