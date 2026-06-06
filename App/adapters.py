from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import redirect
from App.models import UserProfile

User = get_user_model()

class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """Link Google login to an existing account with the same email."""
        print(f"pre_social_login called: is_existing={sociallogin.is_existing}")
        if sociallogin.is_existing:
            return
        email = None
        if sociallogin.email_addresses:
            email = sociallogin.email_addresses[0].email
            print(f"Email from sociallogin.email_addresses: {email}")
        if not email and sociallogin.account:
            email = sociallogin.account.extra_data.get('email')
            print(f"Email from extra_data: {email}")
        if not email:
            print("No email found, skipping user linking")
            return
        try:
            user = User.objects.get(email__iexact=email)
            print(f"Found existing user: {user}")
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            print(f"No existing user found with email: {email}")

    def save_user(self, request, sociallogin, form=None):
        print(f"save_user called for user: {sociallogin.user}")
        user = super().save_user(request, sociallogin, form=form)
        print(f"User saved: {user}")
        UserProfile.objects.get_or_create(user=user, defaults={'balance': 0.00})
        return user

    def on_authentication_error(
        self,
        request,
        provider,
        error=None,
        exception=None,
        extra_context=None,
    ):
        print(f"Authentication error: provider={provider}, error={error}, exception={exception}")
        messages.error(
            request,
            'Google sign-in failed. Please try again or use a different Google account.',
        )
        raise ImmediateHttpResponse(redirect('login'))
