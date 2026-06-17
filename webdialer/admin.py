from django.contrib import admin
from App.models import UserProfile, VirtualNumber, Message, CallLog, CreditTransaction

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'phone', 'created_at']
    search_fields = ['user__username', 'phone']

@admin.register(VirtualNumber)
class VirtualNumberAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'country', 'status', 'renewal_date', 'created_at']
    search_fields = ['phone_number', 'country', 'user__username']
    list_filter = ['status', 'country']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'from_number', 'to_number', 'direction', 'status', 'created_at', 'is_read']
    search_fields = ['from_number', 'to_number', 'message']
    list_filter = ['direction', 'status', 'is_read', 'created_at']

@admin.register(CallLog)
class CallLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'from_number', 'to_number', 'direction', 'status', 'duration', 'cost', 'created_at']
    search_fields = ['from_number', 'to_number', 'telnyx_call_id']
    list_filter = ['direction', 'status', 'created_at']

@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'transaction_type', 'amount', 'description', 'balance_after', 'timestamp']
    search_fields = ['description', 'user__username']
    list_filter = ['transaction_type', 'timestamp']
