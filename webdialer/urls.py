from django.urls import path
from . import views

app_name = 'webdialer'

urlpatterns = [
    path('', views.sms_view, name='sms'),
    path('history/', views.history_view, name='history'),
    path('phone-numbers/', views.phone_numbers_view, name='phone_numbers'),
    path('account/', views.account_view, name='account'),
    path('account/balance-transfer/', views.balance_transfer_view, name='balance_transfer'),
    path('account/payment/', views.payment_view, name='payment'),
    path('help/', views.help_view, name='help'),
    path('send-sms/', views.send_sms_view, name='send_sms'),
    path('billing/initialize/', views.initialize_payment, name='initialize_payment'),
    path('billing/verify/', views.verify_payment, name='verify_payment'),
    path('billing/webhook/', views.paystack_webhook, name='paystack_webhook'),
]
