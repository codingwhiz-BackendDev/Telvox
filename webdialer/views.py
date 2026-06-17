from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from decimal import Decimal
from datetime import datetime, timedelta
import requests
import json
from App.models import UserProfile, VirtualNumber, Message, CallLog, CreditTransaction, PhoneNumberPlan, PhoneNumberInventory, PhoneNumberPurchase
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
def dialer_view(request):
    user = request.user
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user, balance=0.00)
    
    context = {
        'user': user,
    }
    return render(request, 'dialer.html', context)

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

# Telnyx API Integration
def get_telnyx_headers():
    """Get headers for Telnyx API requests"""
    return {
        'Authorization': f'Bearer {settings.TELNYX_API_KEY}',
        'Content-Type': 'application/json',
    }

def fetch_available_numbers(country, number_type='mobile', region=None):
    """Fetch available phone numbers from Telnyx API"""
    try:
        # Map country codes to Telnyx country codes and phone codes
        country_mapping = {
            'US': {'telnyx_code': 'US', 'phone_code': '+1'},
            'AU': {'telnyx_code': 'AU', 'phone_code': '+61'},
            'CA': {'telnyx_code': 'CA', 'phone_code': '+1'},
            'UK': {'telnyx_code': 'GB', 'phone_code': '+44'},
        }
        
        country_info = country_mapping.get(country, {'telnyx_code': country, 'phone_code': '+1'})
        telnyx_country = country_info['telnyx_code']
        phone_code = country_info['phone_code']
        
        url = 'https://api.telnyx.com/v2/available_phone_numbers'
        headers = get_telnyx_headers()
        
        params = {
            'country_code': telnyx_country,
            'limit': 10,
        }
        
        if number_type == 'mobile':
            params['phone_type'] = 'mobile'
        
        if region and region != 'All':
            # Clean region name for API
            clean_region = region.split('(')[0].strip() if '(' in region else region
            params['region'] = clean_region
        
        print(f"Fetching numbers from Telnyx: country={telnyx_country}, params={params}")
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        print(f"Telnyx API response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            numbers = data.get('data', [])
            print(f"Telnyx returned {len(numbers)} numbers")
            
            # Add country code to each number if not already present
            for num in numbers:
                phone_number = num.get('phone_number', '')
                # Only add country code if number doesn't already have one
                if phone_number and not phone_number.startswith('+'):
                    num['phone_number'] = f"{phone_code}{phone_number}"
                print(f"Number: {num.get('phone_number')}, Region: {num.get('region', 'N/A')}")
            return numbers
        else:
            print(f"Telnyx API error: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Error fetching numbers from Telnyx: {e}")
        import traceback
        traceback.print_exc()
        return []

def purchase_telnyx_number(phone_number):
    """Purchase a phone number from Telnyx"""
    try:
        url = 'https://api.telnyx.com/v2/number_orders'
        headers = get_telnyx_headers()
        
        data = {
            'phone_numbers': [
                {
                    'phone_number': phone_number,
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Telnyx purchase error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error purchasing number from Telnyx: {e}")
        return None

@login_required
def buy_phone_number_view(request):
    """View for buying phone numbers"""
    user = request.user
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user, balance=0.00)
    
    # Get or create default plans
    monthly_plan, _ = PhoneNumberPlan.objects.get_or_create(
        plan_type='monthly',
        defaults={
            'price': 1.99,
            'setup_fee': 0.99,
            'features': ['Free voicemail included', 'Free incoming calls & SMS', 'No commitment required']
        }
    )
    
    yearly_plan, _ = PhoneNumberPlan.objects.get_or_create(
        plan_type='yearly',
        defaults={
            'price': 15.00,
            'setup_fee': 0.99,
            'features': ['Free voicemail included', 'Free incoming calls & SMS', 'No commitment required']
        }
    )
    
    context = {
        'user': user,
        'monthly_plan': monthly_plan,
        'yearly_plan': yearly_plan,
    }
    return render(request, 'buy_phone_number.html', context)

@login_required
def get_available_numbers(request):
    """API endpoint to get available numbers from Telnyx"""
    if request.method == 'GET':
        country = request.GET.get('country')
        number_type = request.GET.get('number_type', 'mobile')
        region = request.GET.get('region')
        
        if not country:
            return JsonResponse({'error': 'Country is required'}, status=400)
        
        # Try to get from inventory first
        inventory_numbers = PhoneNumberInventory.objects.filter(
            country=country,
            number_type=number_type,
            is_available=True
        )
        
        if region:
            inventory_numbers = inventory_numbers.filter(region=region)
        
        if inventory_numbers.exists():
            numbers = [
                {
                    'phone_number': num.phone_number,
                    'region': num.region,
                    'locality': num.region,
                }
                for num in inventory_numbers[:10]
            ]
            return JsonResponse({'numbers': numbers})
        
        # If no inventory numbers, fetch from Telnyx
        telnyx_numbers = fetch_available_numbers(country, number_type, region)
        
        if telnyx_numbers:
            numbers = [
                {
                    'phone_number': num.get('phone_number'),
                    'region': num.get('region', ''),
                    'locality': num.get('locality', ''),
                }
                for num in telnyx_numbers
            ]
            return JsonResponse({'numbers': numbers})
        
        return JsonResponse({'numbers': []})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def purchase_phone_number(request):
    """Process phone number purchase"""
    if request.method == 'POST':
        user = request.user
        try:
            profile = user.userprofile
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'User profile not found'}, status=404)
        
        phone_number = request.POST.get('phone_number')
        country = request.POST.get('country')
        plan_type = request.POST.get('plan_type', 'monthly')
        
        if not phone_number or not country:
            return JsonResponse({'error': 'Phone number and country are required'}, status=400)
        
        # Get plan details
        try:
            plan = PhoneNumberPlan.objects.get(plan_type=plan_type)
        except PhoneNumberPlan.DoesNotExist:
            return JsonResponse({'error': 'Invalid plan type'}, status=400)
        
        total_amount = plan.price + plan.setup_fee
        
        # Check if user has sufficient balance
        if profile.balance < total_amount:
            return JsonResponse({'error': f'Insufficient balance. You need ${total_amount:.2f} but have ${profile.balance:.2f}'}, status=400)
        
        # Check if number is already in inventory
        inventory_number = PhoneNumberInventory.objects.filter(
            phone_number=phone_number,
            is_available=True
        ).first()
        
        if not inventory_number:
            # Purchase from Telnyx
            telnyx_response = purchase_telnyx_number(phone_number)
            if not telnyx_response:
                return JsonResponse({'error': 'Failed to purchase number from Telnyx'}, status=500)
            
            # Create inventory record
            inventory_number = PhoneNumberInventory.objects.create(
                country=country,
                number_type='mobile',
                phone_number=phone_number,
                is_available=False,
                telnyx_number_id=telnyx_response.get('data', {}).get('phone_numbers', [{}])[0].get('id')
            )
        else:
            # Mark as unavailable
            inventory_number.is_available = False
            inventory_number.save()
        
        # Calculate expiry date
        if plan_type == 'monthly':
            expiry_date = datetime.now() + timedelta(days=30)
        else:
            expiry_date = datetime.now() + timedelta(days=365)
        
        # Deduct from user balance
        profile.balance -= total_amount
        profile.save()
        
        # Create purchase record
        purchase = PhoneNumberPurchase.objects.create(
            user=user,
            phone_number=inventory_number,
            plan=plan_type,
            amount_paid=total_amount,
            expiry_date=expiry_date
        )
        
        # Create transaction record
        CreditTransaction.objects.create(
            user=user,
            transaction_type='debit',
            amount=total_amount,
            description=f'Phone number purchase - {phone_number} ({plan_type} plan)',
            balance_after=profile.balance
        )
        
        # Create or update virtual number record
        VirtualNumber.objects.update_or_create(
            user=user,
            phone_number=phone_number,
            defaults={
                'country': inventory_number.get_country_display(),
                'status': 'active',
                'renewal_date': expiry_date
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Phone number purchased successfully',
            'phone_number': phone_number,
            'expiry_date': expiry_date.strftime('%Y-%m-%d')
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
