from django.urls import path
from . import views


app_name = 'payment'

urlpatterns = [
    path('pay/<uuid:unique_id>/', views.payment_page, name='payment_page'),
    path('pay/<uuid:unique_id>/create-invoice/', views.create_invoice, name='create_invoice'),
    path('pay/<uuid:unique_id>/consent/', views.record_consent, name='record_consent'),
    path('webhook/monobank/', views.monobank_webhook, name='monobank_webhook'),
    path('pay/<uuid:unique_id>/success/', views.payment_success, name='payment_success'),
    path('pay/<uuid:unique_id>/failure/', views.payment_failure, name='payment_failure'),
]

