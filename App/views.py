from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout, login as auth_login
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.hashers import make_password
from .models import UserProfile
from .tokens import email_verification_token, password_reset_token

def index(request):
    return render(request, 'index.html')

def login(request):
    if request.user.is_authenticated:
        return redirect('webdialer:sms')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '').strip()
        
        if not email or not password:
            messages.error(request, "Please enter your email and password.")
            return render(request, 'login.html')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "No account found with that email address.")
            return render(request, 'login.html')
        
        if not user.is_active:
            messages.error(request, "Please verify your email before signing in.")
            return render(request, 'login.html')
        
        if not user.check_password(password):
            messages.error(request, "Incorrect password. Please try again.")
            return render(request, 'login.html')
        
        auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('webdialer:sms')
    
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '').strip()
        password2 = request.POST.get('confirm_password', '').strip()
        
        if not first_name or not last_name:
            messages.error(request, "First and last name are required.")
            return render(request, 'register.html')
        
        if not email:
            messages.error(request, "Email address is required.")
            return render(request, 'register.html')
        
        if not password or not password2:
            messages.error(request, "Please fill in both password fields.")
            return render(request, 'register.html')
        
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Please enter a valid email address.")
            return render(request, 'register.html')
        
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return render(request, 'register.html')
        
        if password != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "An account with that email already exists.")
            return render(request, 'register.html')
        
        base_username = f"{first_name}_{last_name}".lower()
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        user = User.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=make_password(password),
            is_active=True,  # Activate immediately without email verification
        )

        # Create user profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.is_email_verified = True  # Mark as verified since we're skipping email verification
        profile.save()

        # Log the user in immediately
        auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, "Account created successfully!")
        return redirect('webdialer:sms')
    
    return render(request, 'register.html')

def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        return render(request, 'verify_result.html', {
            'status': 'invalid',
            'heading': 'Invalid link',
            'message': 'Verification link is invalid.',
        })
    
    if email_verification_token.check_token(user, token):
        user.is_active = True
        user.save()
        
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.is_email_verified = True
        profile.save()
        
        return render(request, 'verify_result.html', {
            'status': 'success',
            'heading': 'Email verified',
            'message': 'Your account is now active.',
        })
    
    return render(request, 'verify_result.html', {
        'status': 'expired',
        'heading': 'Link expired',
        'message': 'Verification link expired.',
    })

def resend_verification(request):
    if request.method != 'POST':
        return redirect('register')
    
    email = request.POST.get('email', '').strip().lower()
    
    try:
        user = User.objects.get(email=email, is_active=False)
    except User.DoesNotExist:
        return render(request, 'verify_pending.html', {'email': email})
    
    try:
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_verification_token.make_token(user)
        domain = get_current_site(request).domain
        
        verification_link = f"http://{domain}/verify-email/{uid}/{token}/"
        
        send_mail(
            "Verify your SAMAPPTECH account",
            f"Click here to verify:\n{verification_link}",
            "noreply@samapptech.com",
            [email],
            fail_silently=False,
        )
    except Exception:
        messages.error(request, "Could not resend email.")
        return render(request, 'verify_pending.html', {'email': email})
    
    return render(request, 'verify_pending.html', {'email': email, 'resent': True})

def logout(request):
    auth_logout(request)
    return redirect('index')

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()

        if not email:
            messages.error(request, "Please enter your email.")
            return render(request, "forgot_password.html")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "No account found with that email.")
            return render(request, "forgot_password.html")

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = password_reset_token.make_token(user)
        domain = get_current_site(request).domain

        reset_link = f"http://{domain}/reset-password/{uid}/{token}/"

        send_mail(
            "Reset your SAMAPPTECH password",
            f"Click the link below to reset your password:\n\n{reset_link}",
            "noreply@samapptech.com",
            [email],
            fail_silently=False,
        )

        return render(request, "reset_email_sent.html", {"email": email})

    return render(request, "forgot_password.html")

def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        return render(request, "reset_result.html", {
            "status": "invalid",
            "message": "Invalid reset link."
        })

    if not password_reset_token.check_token(user, token):
        return render(request, "reset_result.html", {
            "status": "expired",
            "message": "Reset link expired."
        })

    if request.method == "POST":
        password = request.POST.get("password", "").strip()
        confirm = request.POST.get("confirm_password", "").strip()

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return render(request, "reset_password.html")

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, "reset_password.html")

        user.password = make_password(password)
        user.save()

        return render(request, "reset_result.html", {
            "status": "success",
            "message": "Your password has been reset successfully."
        })

    return render(request, "reset_password.html") 

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def profile(request):
    return render(request, 'profile.html')

@login_required
def account_settings(request):
    return render(request, 'settings.html')

def help(request):
    return render(request, 'help.html')

def privacy(request):
    return render(request, 'privacy.html')

def terms(request):
    return render(request, 'terms.html')

def contact(request):
    return render(request, 'contact.html')

def google_login_redirect(request):
    """Use allauth's built-in Google OAuth flow (handles callback + signup)."""
    return redirect(reverse('google_login'))
