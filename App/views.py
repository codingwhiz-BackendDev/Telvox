from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.urls import reverse

def index(request):
    return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')

def logout(request):
    auth_logout(request)
    return redirect('index') 

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
