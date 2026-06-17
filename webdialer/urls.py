from django.urls import path
from . import views

app_name = 'webdialer'

urlpatterns = [
    path('', views.sms_view, name='sms'),
    path('history/', views.history_view, name='history'),
    path('phone-numbers/', views.phone_numbers_view, name='phone_numbers'),
    path('buy-phone-number/', views.buy_phone_number_view, name='buy_phone_number'),
    path('get-available-numbers/', views.get_available_numbers, name='get_available_numbers'),
    path('purchase-phone-number/', views.purchase_phone_number, name='purchase_phone_number'),
    path('dialer/', views.dialer_view, name='dialer'),
    path('account/', views.account_view, name='account'),
    path('account/balance-transfer/', views.balance_transfer_view, name='balance_transfer'),
    path('account/payment/', views.payment_view, name='payment'),
    path('help/', views.help_view, name='help'),
    path('send-sms/', views.send_sms_view, name='send_sms'),
    path('voice-call/', views.voice_call_view, name='voice_call'),
    path('sms-history/', views.sms_history_view, name='sms_history'),
    path('call-history/', views.call_history_view, name='call_history'),
    path('sms-webhook/', views.sms_webhook_view, name='sms_webhook'),
    path('call-webhook/', views.call_webhook_view, name='call_webhook'),
    path('billing/initialize/', views.initialize_payment, name='initialize_payment'),
    path('billing/verify/', views.verify_payment, name='verify_payment'),
    path('billing/webhook/', views.paystack_webhook, name='paystack_webhook'),
]
