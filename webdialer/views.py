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
    messages = Message.objects.filter(user=user).order_by('-created_at')
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
                'last_message': msg.message,
                'last_message_time': msg.created_at
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
        ).order_by('created_at')
    
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
            Q(from_number__icontains=search_query) | 
            Q(to_number__icontains=search_query)
        )
    
    call_logs = call_logs.order_by('-created_at')
    
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
        
        # Use available_phone_numbers endpoint
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
            print(f"Sample number data: {numbers[0] if numbers else 'None'}")
            
            # Process numbers - search endpoint returns actual unmasked numbers
            processed_numbers = []
            for num in numbers:
                # Get phone number ID for purchasing
                phone_number_id = num.get('id', '')
                
                # Get the actual phone number
                phone_number = num.get('phone_number', '')
                
                # Only add country code if number doesn't already have one
                if phone_number and not phone_number.startswith('+'):
                    phone_number = f"{phone_code}{phone_number}"
                
                processed_num = {
                    'phone_number': phone_number,
                    'phone_number_id': phone_number_id,  # Store ID for purchasing
                    'region': num.get('region', ''),
                    'locality': num.get('locality', num.get('region', ''))
                }
                processed_numbers.append(processed_num)
                print(f"Processed Number: {phone_number}, ID: {phone_number_id}, Region: {num.get('region', 'N/A')}")
            
            return processed_numbers
        else:
            print(f"Telnyx API error: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Error fetching numbers from Telnyx: {e}")
        import traceback
        traceback.print_exc()
        return []

def send_telnyx_sms(from_number, to_number, message):
    """Send SMS via Telnyx API"""
    try:
        url = 'https://api.telnyx.com/v2/messages'
        headers = get_telnyx_headers()
        
        data = {
            'from': from_number,
            'to': to_number,
            'text': message,
            'type': 'text'
        }
        
        print(f"Sending SMS via Telnyx: from={from_number}, to={to_number}")
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        print(f"Telnyx SMS API response status: {response.status_code}")
        
        if response.status_code in [200, 201, 202]:
            response_data = response.json()
            message_id = response_data.get('data', {}).get('id')
            print(f"SMS sent successfully: {message_id}")
            return response_data
        else:
            error_detail = response.text
            try:
                error_json = response.json()
                error_detail = error_json.get('errors', [{}])[0].get('detail', error_detail)
            except:
                pass
            print(f"Telnyx SMS API error: {response.status_code} - {error_detail}")
            return None
    except requests.exceptions.Timeout:
        print("Telnyx SMS API timeout")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Telnyx SMS API request error: {e}")
        return None
    except Exception as e:
        print(f"Error sending SMS via Telnyx: {e}")
        import traceback
        traceback.print_exc()
        return None

def initiate_telnyx_call(from_number, to_number):
    """Initiate a voice call via Telnyx API"""
    try:
        url = 'https://api.telnyx.com/v2/calls'
        headers = get_telnyx_headers()
        
        data = {
            'from': from_number,
            'to': to_number,
            'connection_id': settings.TELNYX_CONNECTION_ID if hasattr(settings, 'TELNYX_CONNECTION_ID') else '',
            'webhook_url': f"{settings.SITE_URL}/webdialer/call-webhook/"
        }
        
        print(f"Initiating call via Telnyx: from={from_number}, to={to_number}")
        print(f"Connection ID: {data.get('connection_id', 'Not set')}")
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        print(f"Telnyx Call API response status: {response.status_code}")
        
        if response.status_code in [200, 201, 202]:
            response_data = response.json()
            call_id = response_data.get('data', {}).get('id')
            print(f"Call initiated successfully: {call_id}")
            return response_data
        else:
            error_detail = response.text
            try:
                error_json = response.json()
                error_detail = error_json.get('errors', [{}])[0].get('detail', error_detail)
            except:
                pass
            print(f"Telnyx Call API error: {response.status_code} - {error_detail}")
            return None
    except requests.exceptions.Timeout:
        print("Telnyx Call API timeout")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Telnyx Call API request error: {e}")
        return None
    except Exception as e:
        print(f"Error initiating call via Telnyx: {e}")
        import traceback
        traceback.print_exc()
        return None

def reserve_telnyx_number(phone_number):
    """Reserve a phone number from Telnyx to get the actual unmasked number"""
    try:
        # According to Telnyx docs, you can reserve by including the number in a number order
        # The number will be reserved and you'll get the actual number in the response
        url = 'https://api.telnyx.com/v2/number_orders'
        headers = get_telnyx_headers()
        
        data = {
            'phone_numbers': [
                {
                    'phone_number': phone_number
                }
            ]
        }
        
        print(f"Reserving phone number via order: {phone_number}")
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code in [200, 201]:
            result = response.json()
            # Get the actual phone number from the order response
            ordered_numbers = result.get('data', {}).get('phone_numbers', [])
            if ordered_numbers:
                actual_number = ordered_numbers[0].get('phone_number', phone_number)
                print(f"Reserved actual phone number: {actual_number}")
                return actual_number
            return phone_number
        else:
            print(f"Telnyx reservation error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error reserving number from Telnyx: {e}")
        return None

def purchase_telnyx_number(phone_number, phone_number_id=None):
    """Purchase a phone number from Telnyx"""
    try:
        url = 'https://api.telnyx.com/v2/number_orders'
        headers = get_telnyx_headers()
        
        # If phone number is masked, try to reserve it first
        if phone_number and ('-' in phone_number or '*' in phone_number):
            print(f"Phone number is masked, attempting to reserve: {phone_number}")
            actual_number = reserve_telnyx_number(phone_number)
            if actual_number:
                phone_number = actual_number
            else:
                print("Failed to reserve masked phone number")
                return None
        
        # Use phone_number_id if available, otherwise use phone_number
        if phone_number_id:
            data = {
                'phone_numbers': [
                    {
                        'phone_number_id': phone_number_id,
                    }
                ]
            }
            print(f"Purchasing number using ID: {phone_number_id}")
        else:
            data = {
                'phone_numbers': [
                    {
                        'phone_number': phone_number,
                    }
                ]
            }
            print(f"Purchasing number using phone number: {phone_number}")
        
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
def send_sms_view(request):
    """View for sending SMS messages"""
    user = request.user
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user, balance=0.00)
    
    # Get user's virtual numbers
    virtual_numbers = VirtualNumber.objects.filter(user=user, status='active')
    
    if request.method == 'POST':
        from_number = request.POST.get('from_number')
        to_number = request.POST.get('to_number')
        message = request.POST.get('message')
        
        if not from_number or not to_number or not message:
            return JsonResponse({'error': 'All fields are required'}, status=400)
        
        # Validate phone number format
        if not to_number.startswith('+'):
            return JsonResponse({'error': 'Phone number must include country code (e.g., +1234567890)'}, status=400)
        
        # Calculate SMS cost (assuming $0.01 per SMS segment, 160 chars per segment)
        message_length = len(message)
        segments = max(1, (message_length + 159) // 160)  # Round up to nearest segment
        sms_cost = Decimal('0.01') * Decimal(str(segments))
        
        # Refresh profile from database to get latest balance
        profile.refresh_from_db()
        
        # Check if user has sufficient balance
        if profile.balance < sms_cost:
            return JsonResponse({'error': f'Insufficient balance. You need ${sms_cost:.2f} but have ${profile.balance:.2f}'}, status=400)
        
        # Send SMS via Telnyx
        telnyx_response = send_telnyx_sms(from_number, to_number, message)
        
        if telnyx_response:
            # Refresh profile again and deduct balance
            profile.refresh_from_db()
            profile.balance -= sms_cost
            profile.save()
            
            # Create message record
            Message.objects.create(
                user=user,
                from_number=from_number,
                to_number=to_number,
                message=message,
                direction='outbound',
                status='sent'
            )
            
            # Create transaction record
            CreditTransaction.objects.create(
                user=user,
                transaction_type='debit',
                amount=sms_cost,
                description=f'SMS sent to {to_number}',
                balance_after=profile.balance
            )
            
            return JsonResponse({'success': True, 'message': 'SMS sent successfully', 'cost': float(sms_cost), 'segments': segments})
        else:
            return JsonResponse({'error': 'Failed to send SMS via Telnyx. Please check your API credentials and try again.'}, status=500)
    
    context = {
        'user': user,
        'virtual_numbers': virtual_numbers,
        'balance': profile.balance
    }
    return render(request, 'send_sms.html', context)

@login_required
def voice_call_view(request):
    """View for making voice calls"""
    user = request.user
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user, balance=0.00)
    
    # Get user's virtual numbers
    virtual_numbers = VirtualNumber.objects.filter(user=user, status='active')
    
    if request.method == 'POST':
        from_number = request.POST.get('from_number')
        to_number = request.POST.get('to_number')
        
        if not from_number or not to_number:
            return JsonResponse({'error': 'Both numbers are required'}, status=400)
        
        # Validate phone number format
        if not to_number.startswith('+'):
            return JsonResponse({'error': 'Phone number must include country code (e.g., +1234567890)'}, status=400)
        
        # Calculate call cost (assuming $0.02 per minute)
        call_cost_per_minute = Decimal('0.02')
        minimum_charge = call_cost_per_minute  # Minimum 1 minute charge
        
        # Refresh profile from database to get latest balance
        profile.refresh_from_db()
        
        # Check if user has sufficient balance (minimum 1 minute)
        if profile.balance < minimum_charge:
            return JsonResponse({'error': f'Insufficient balance. You need at least ${minimum_charge:.2f} for 1 minute call'}, status=400)
        
        # Initiate call via Telnyx
        telnyx_response = initiate_telnyx_call(from_number, to_number)
        
        if telnyx_response:
            call_id = telnyx_response.get('data', {}).get('id')
            
            # Refresh profile again and deduct balance
            profile.refresh_from_db()
            profile.balance -= minimum_charge
            profile.save()
            
            # Create call log record
            CallLog.objects.create(
                user=user,
                from_number=from_number,
                to_number=to_number,
                direction='outbound',
                status='initiated',
                telnyx_call_id=call_id,
                cost=minimum_charge  # Initial cost, will be updated after call ends
            )
            
            # Create transaction record
            CreditTransaction.objects.create(
                user=user,
                transaction_type='debit',
                amount=minimum_charge,
                description=f'Voice call initiated to {to_number}',
                balance_after=profile.balance
            )
            
            return JsonResponse({'success': True, 'message': 'Call initiated successfully', 'call_id': call_id, 'cost': float(minimum_charge)})
        else:
            return JsonResponse({'error': 'Failed to initiate call via Telnyx. Please check your API credentials and connection settings.'}, status=500)
    
    context = {
        'user': user,
        'virtual_numbers': virtual_numbers,
        'balance': profile.balance
    }
    return render(request, 'voice_call.html', context)

@csrf_exempt
def sms_webhook_view(request):
    """Webhook endpoint for Telnyx inbound SMS"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Telnyx sends SMS data in different formats depending on webhook type
            payload = data.get('data', {}).get('payload', {})
            
            # Try different possible field names for phone numbers
            from_number = payload.get('from', payload.get('from_number', {}))
            to_number = payload.get('to', payload.get('to_number', {}))
            
            # Try different possible field names for message content
            message = payload.get('text', payload.get('content', payload.get('body', '')))
            
            # Handle nested phone number objects
            if isinstance(from_number, dict):
                from_number = from_number.get('phone_number', from_number.get('phone_number', ''))
            if isinstance(to_number, dict):
                to_number = to_number.get('phone_number', to_number.get('phone_number', ''))
            
            # Also check if numbers are directly in the payload
            if not from_number:
                from_number = data.get('data', {}).get('payload', {}).get('from', {}).get('phone_number', '')
            if not to_number:
                to_number = data.get('data', {}).get('payload', {}).get('to', {}).get('phone_number', '')
            
            print(f"SMS webhook received: from={from_number}, to={to_number}, message={message}")
            
            if from_number and to_number and message:
                # Find the user who owns the virtual number
                virtual_number = VirtualNumber.objects.filter(phone_number=to_number, status='active').first()
                if virtual_number:
                    # Create inbound message record
                    Message.objects.create(
                        user=virtual_number.user,
                        from_number=from_number,
                        to_number=to_number,
                        message=message,
                        direction='inbound',
                        status='received'
                    )
                    print(f"Created inbound message for user {virtual_number.user.username}")
                else:
                    print(f"Virtual number {to_number} not found")
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            print(f"Error processing SMS webhook: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'status': 'error'}, status=500)
    
    return JsonResponse({'status': 'invalid method'}, status=405)

@csrf_exempt
def call_webhook_view(request):
    """Webhook endpoint for Telnyx call events (both inbound and outbound)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            event_type = data.get('data', {}).get('event_type', '')
            payload = data.get('data', {}).get('payload', {})
            
            print(f"Call webhook received: event_type={event_type}")
            
            # Handle inbound call initiation
            if event_type == 'call.initiated':
                from_number = payload.get('from', {})
                to_number = payload.get('to', {})
                call_id = payload.get('call_id')
                
                # Handle nested phone number objects
                if isinstance(from_number, dict):
                    from_number = from_number.get('phone_number', '')
                if isinstance(to_number, dict):
                    to_number = to_number.get('phone_number', '')
                
                print(f"Inbound call initiated: from={from_number}, to={to_number}, call_id={call_id}")
                
                if from_number and to_number:
                    # Find the user who owns the virtual number
                    virtual_number = VirtualNumber.objects.filter(phone_number=to_number, status='active').first()
                    if virtual_number:
                        # Create inbound call log
                        CallLog.objects.create(
                            user=virtual_number.user,
                            from_number=from_number,
                            to_number=to_number,
                            direction='inbound',
                            status='ringing',
                            telnyx_call_id=call_id
                        )
                        print(f"Created inbound call log for user {virtual_number.user.username}")
            
            # Handle call status updates (for outbound calls)
            call_id = payload.get('call_id')
            call_status = payload.get('call_status')
            call_duration = payload.get('call_duration')
            
            if call_id and call_status:
                print(f"Call status update: call_id={call_id}, status={call_status}, duration={call_duration}")
                
                # Update call log with new status
                call_log = CallLog.objects.filter(telnyx_call_id=call_id).first()
                if call_log:
                    call_log.status = call_status.lower()
                    if call_duration:
                        call_log.duration = int(call_duration)
                        # Calculate actual cost based on duration (only for outbound calls)
                        if call_log.direction == 'outbound':
                            cost_per_minute = Decimal('0.02')
                            actual_cost = cost_per_minute * Decimal(str(call_duration))
                            initial_cost = call_log.cost
                            cost_difference = actual_cost - initial_cost
                            
                            # Update call log cost
                            call_log.cost = actual_cost
                            
                            # If actual cost is different from initial cost, adjust user balance
                            if cost_difference != 0:
                                user = call_log.user
                                try:
                                    profile = user.userprofile
                                    profile.balance -= cost_difference  # Negative if refund needed
                                    profile.save()
                                    
                                    # Create transaction record for adjustment
                                    CreditTransaction.objects.create(
                                        user=user,
                                        transaction_type='debit' if cost_difference > 0 else 'credit',
                                        amount=abs(cost_difference),
                                        description=f'Call cost adjustment for {call_log.to_number}',
                                        balance_after=profile.balance
                                    )
                                    print(f"Adjusted user balance by ${cost_difference:.2f}")
                                except UserProfile.DoesNotExist:
                                    print(f"User profile not found for balance adjustment")
                    
                    call_log.save()
                    print(f"Updated call log: {call_log.id}")
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            print(f"Error processing call webhook: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'status': 'error'}, status=500)
    
    return JsonResponse({'status': 'invalid method'}, status=405)

@login_required
def sms_history_view(request):
    """View for SMS history"""
    user = request.user
    messages = Message.objects.filter(user=user).order_by('-created_at')
    
    context = {
        'user': user,
        'messages': messages
    }
    return render(request, 'sms_history.html', context)

@login_required
def call_history_view(request):
    """View for call history"""
    user = request.user
    calls = CallLog.objects.filter(user=user).order_by('-created_at')
    
    context = {
        'user': user,
        'calls': calls
    }
    return render(request, 'call_history.html', context)

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
        phone_number_id = request.POST.get('phone_number_id', '')
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
            telnyx_response = purchase_telnyx_number(phone_number, phone_number_id)
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
