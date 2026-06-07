from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from decimal import Decimal
import requests
import json
from App.models import UserProfile, VirtualNumber, Message, CallLog, CreditTransaction
from django.db.models import Q

def get_usd_to_naira_rate():
    """
    Fetch current USD to NGN exchange rate from API.
    Caches the rate for 1 hour to avoid excessive API calls.
    Falls back to a default rate if API fails.
    """
    # Try to get cached rate first
    cached_rate = cache.get('usd_to_naira_rate')
    if cached_rate:
        return cached_rate
    
    try:
        # Use a free exchange rate API
        response = requests.get('https://api.exchangerate-api.com/v4/latest/USD', timeout=5)
        if response.status_code == 200:
            data = response.json()
            rate = data.get('rates', {}).get('NGN', 1360)  # Default to 1360 if NGN not found
            
            # Cache the rate for 1 hour (3600 seconds)
            cache.set('usd_to_naira_rate', rate, 3600)
            return rate
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
    
    # Fallback to default rate if API fails
    return 1360

@login_required
def sms_view(request):
    user = request.user
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user, balance=0.00)
    
    virtual_numbers = VirtualNumber.objects.filter(user=user, status='active')
    active_virtual_number = virtual_numbers.first().phone_number if virtual_numbers else None
    
    # Get all messages and group by conversation
    messages = Message.objects.filter(user=user).order_by('-timestamp')
    conversations = []
    seen_numbers = set()
    
    for msg in messages:
        if msg.direction == 'inbound':
            contact_number = msg.from_number
        else:
            contact_number = msg.to_number
        
        if contact_number not in seen_numbers:
            seen_numbers.add(contact_number)
            conversations.append({
                'id': contact_number,
                'contact_number': contact_number,
                'last_message': msg.content,
                'last_message_time': msg.timestamp
            })
    
    active_conversation_id = request.GET.get('conversation')
    active_conversation = None
    conversation_messages = []
    
    if active_conversation_id:
        active_conversation = next((c for c in conversations if c['id'] == active_conversation_id), None)
        conversation_messages = Message.objects.filter(
            user=user
        ).filter(
            Q(from_number=active_conversation_id) | Q(to_number=active_conversation_id)
        ).order_by('timestamp')
    
    context = {
        'user': user,
        'conversations': conversations,
        'active_conversation_id': active_conversation_id,
        'active_conversation': active_conversation,
        'messages': conversation_messages,
        'active_virtual_number': active_virtual_number,
    }
    return render(request, 'sms.html', context)

@login_required
def history_view(request):
    user = request.user
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user, balance=0.00)
    
    search_query = request.GET.get('search', '')
    call_logs = CallLog.objects.filter(user=user)
    
    if search_query:
        call_logs = call_logs.filter(
            Q(caller_number__icontains=search_query) | 
            Q(did_number__icontains=search_query)
        )
    
    call_logs = call_logs.order_by('-timestamp')
    
    paginator = Paginator(call_logs, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'user': user,
        'call_logs': page_obj,
        'search_query': search_query,
    }
    return render(request, 'history.html', context)

@login_required
def phone_numbers_view(request):
    user = request.user
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user, balance=0.00)
    
    virtual_numbers = VirtualNumber.objects.filter(user=user)
    
    context = {
        'user': user,
        'virtual_numbers': virtual_numbers,
    }
    return render(request, 'phone_numbers.html', context)

@login_required
def account_view(request):
    user = request.user
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user, balance=0.00)
    
    virtual_numbers = VirtualNumber.objects.filter(user=user)
    transactions = CreditTransaction.objects.filter(user=user).order_by('-timestamp')
    active_tab = request.GET.get('tab', 'buy_credits')
    
    context = {
        'user': user,
        'virtual_numbers': virtual_numbers,
        'transactions': transactions,
        'active_tab': active_tab,
    }
    return render(request, 'account.html', context)

@login_required
def balance_transfer_view(request):
    user = request.user
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user, balance=0.00)
    
    if request.method == 'POST':
        from_number_id = request.POST.get('from_number')
        to_number_id = request.POST.get('to_number')
        amount = float(request.POST.get('amount', 0))
        
        # Simple validation - in production you'd want more robust validation
        if from_number_id and to_number_id and amount > 0:
            # For now, just redirect back to account page with a success message
            # In production, you'd implement the actual balance transfer logic
            return redirect('webdialer:account', tab='transaction_history')
    
    return redirect('webdialer:account', tab='balance_transfer')

@login_required
def help_view(request):
    user = request.user
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user, balance=0.00)
    
    context = {
        'user': user,
    }
    return render(request, 'help.html', context)

@login_required
def payment_view(request):
    user = request.user
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user, balance=0.00)
    
    context = {
        'user': user,
        'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY,
    }
    return render(request, 'payment.html', context)

@login_required
def initialize_payment(request):
    if request.method == 'POST':
        user = request.user
        try:
            profile = user.userprofile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=user, balance=0.00)
        
        amount = float(request.POST.get('amount', 0))
        bonus = float(request.POST.get('bonus', 0))
        email = user.email
        
        if amount < 5:
            return JsonResponse({'error': 'Minimum amount is $5'}, status=400)
        
        if not settings.PAYSTACK_SECRET_KEY:
            return JsonResponse({'error': 'Paystack secret key not configured. Please add PAYSTACK_SECRET_KEY to your .env file.'}, status=500)
        
        # Get current USD to Naira exchange rate
        usd_to_naira_rate = get_usd_to_naira_rate()
        amount_in_naira = amount * usd_to_naira_rate
        
        total_credits = amount + bonus
        
        # Initialize Paystack transaction
        url = 'https://api.paystack.co/transaction/initialize'
        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json',
        }
        data = {
            'email': email,
            'amount': int(amount_in_naira * 100),  # Paystack expects amount in kobo (cents)
            'callback_url': settings.PAYSTACK_CALLBACK_URL,
            'metadata': {
                'user_id': user.id,
                'amount': amount,
                'bonus': bonus,
                'total_credits': total_credits,
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response_data = response.json()
            
            if response_data.get('status'):
                return JsonResponse({
                    'success': True,
                    'authorization_url': response_data['data']['authorization_url'],
                    'reference': response_data['data']['reference']
                })
            else:
                return JsonResponse({'error': response_data.get('message', 'Payment initialization failed')}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def verify_payment(request):
    if request.method == 'GET':
        reference = request.GET.get('reference')
        
        if not reference:
            return JsonResponse({'error': 'No reference provided'}, status=400)
        
        # Verify transaction with Paystack
        url = f'https://api.paystack.co/transaction/verify/{reference}'
        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        }
        
        try:
            response = requests.get(url, headers=headers)
            response_data = response.json()
            
            if response_data.get('status') and response_data['data']['status'] == 'success':
                # Payment successful, update user balance
                metadata = response_data['data'].get('metadata', {})
                user_id = metadata.get('user_id')
                amount = Decimal(str(metadata.get('amount', 0)))
                bonus = Decimal(str(metadata.get('bonus', 0)))
                total_credits = Decimal(str(metadata.get('total_credits', amount)))
                
                try:
                    user = User.objects.get(id=user_id)
                    profile = user.userprofile
                    profile.balance += total_credits
                    profile.save()
                    
                    # Create transaction record
                    CreditTransaction.objects.create(
                        user=user,
                        transaction_type='topup',
                        amount=total_credits,
                        description=f'Paystack payment - ${amount}{f" + ${bonus} bonus" if bonus > 0 else ""} - {reference}',
                        balance_after=profile.balance
                    )
                    
                    return redirect('/webdialer/account/?tab=transaction_history')
                except User.DoesNotExist:
                    return JsonResponse({'error': 'User not found'}, status=404)
            else:
                return JsonResponse({'error': 'Payment verification failed'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def paystack_webhook(request):
    if request.method == 'POST':
        try:
            # Verify webhook signature (in production, you should verify the signature)
            payload = json.loads(request.body)
            event = payload.get('event')
            
            if event == 'charge.success':
                data = payload.get('data', {})
                reference = data.get('reference')
                metadata = data.get('metadata', {})
                user_id = metadata.get('user_id')
                amount = Decimal(str(metadata.get('amount', 0)))
                bonus = Decimal(str(metadata.get('bonus', 0)))
                total_credits = Decimal(str(metadata.get('total_credits', amount)))
                
                try:
                    user = User.objects.get(id=user_id)
                    profile = user.userprofile
                    profile.balance += total_credits
                    profile.save()
                    
                    # Create transaction record
                    CreditTransaction.objects.create(
                        user=user,
                        transaction_type='topup',
                        amount=total_credits,
                        description=f'Paystack payment - ${amount}{f" + ${bonus} bonus" if bonus > 0 else ""} - {reference}',
                        balance_after=profile.balance
                    )
                except User.DoesNotExist:
                    pass
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def send_sms_view(request):
    if request.method == 'POST':
        user = request.user
        try:
            profile = user.userprofile
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'User profile not found'}, status=404)
        
        to_number = request.POST.get('to_number')
        from_number = request.POST.get('from_number')
        message = request.POST.get('message')
        
        # Check if user has sufficient balance (assuming SMS costs $0.05 per message)
        sms_cost = 0.05
        if profile.balance < sms_cost:
            return JsonResponse({'error': 'Insufficient balance. Please top up your account.'}, status=400)
        
        # Deduct balance
        profile.balance -= sms_cost
        profile.save()
        
        # Create message record
        Message.objects.create(
            user=user,
            from_number=from_number,
            to_number=to_number,
            content=message,
            direction='outbound'
        )
        
        # Create transaction record
        CreditTransaction.objects.create(
            user=user,
            transaction_type='debit',
            amount=sms_cost,
            description=f'SMS to {to_number}',
            balance_after=profile.balance
        )
        
        # Redirect back to SMS page with the conversation
        return redirect(f'/webdialer/?conversation={to_number}')
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
