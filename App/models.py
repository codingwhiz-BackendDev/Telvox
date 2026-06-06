from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class VirtualNumber(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='virtual_numbers')
    country = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('suspended', 'Suspended')], default='active')
    renewal_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone_number} ({self.country})"

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    from_number = models.CharField(max_length=20)
    to_number = models.CharField(max_length=20)
    content = models.TextField()
    direction = models.CharField(max_length=10, choices=[('inbound', 'Inbound'), ('outbound', 'Outbound')])
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.direction}: {self.from_number} -> {self.to_number}"

class CallLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='call_logs')
    caller_number = models.CharField(max_length=20)
    did_number = models.CharField(max_length=20)  # The virtual number that was called
    call_type = models.CharField(max_length=10, choices=[('inbound', 'Inbound'), ('outbound', 'Outbound')])
    duration = models.IntegerField(default=0)  # in seconds
    timestamp = models.DateTimeField(auto_now_add=True)
    recording_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.call_type} call to {self.did_number}"

class CreditTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credit_transactions')
    transaction_type = models.CharField(max_length=10, choices=[('topup', 'Top-up'), ('debit', 'Debit')])
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type}: ${self.amount}"
