from django.urls import path
from . import proposal_views
from . import tz_views
from . import views
from . import webhooks

urlpatterns = [
    # Основні сторінки
    path('', views.HomeView.as_view(), name='home'),
    path('portfolio/', views.PortfolioView.as_view(), name='portfolio'),
    path('calculator/', views.CalculatorView.as_view(), name='calculator'),
    path('developer/', views.DeveloperView.as_view(), name='developer'),
    path('contacts/', views.ContactsView.as_view(), name='contacts'),
    path('offer/', views.OfferView.as_view(), name='offer'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('cookies/', views.CookiesView.as_view(), name='cookies'),
    path('refund/', views.RefundPolicyView.as_view(), name='refund'),
    path('intellectual-property/', views.IntellectualPropertyView.as_view(), name='intellectual_property'),
    path('monobank-chastynamy/', views.MonobankChastView.as_view(), name='monobank_chastynamy'),
    path('internet-shop/', views.InternetShopView.as_view(), name='internet_shop'),
    path('internet-shop-v2/', views.InternetShopV2View.as_view(), name='internet_shop_v2'),
    path('corporate-website-v2/', views.CorporateWebsiteV2View.as_view(), name='corporate_website_v2'),
    path('tz-dlia-saitu/', tz_views.TzGeneratorView.as_view(), name='tz_generator'),
    path('corporate-website/', views.CorporateWebsiteView.as_view(), name='corporate_website'),
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