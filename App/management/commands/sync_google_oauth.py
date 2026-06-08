from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp


class Command(BaseCommand):
    help = 'Sync Google OAuth SocialApp and Site domain for local development'

    def handle(self, *args, **options):
        client_id = settings.GOOGLE_OAUTH2_KEY
        secret = settings.GOOGLE_OAUTH2_SECRET

        if not secret:
            self.stdout.write(self.style.WARNING(
                'GOOGLE_OAUTH2_SECRET is empty. Set it in your .env file.'
            ))

        site, _ = Site.objects.update_or_create(
            pk=settings.SITE_ID,
            defaults={
                'domain': '127.0.0.1:8000',
                'name': 'SAMAPPTECH Local',
            },
        )

        defaults = {'name': 'Google', 'client_id': client_id}
        if secret:
            defaults['secret'] = secret
        app, created = SocialApp.objects.update_or_create(
            provider='google',
            defaults=defaults,
        )
        if not secret and not app.secret:
            self.stdout.write(self.style.ERROR(
                'No client secret in .env or database. OAuth will fail until GOOGLE_OAUTH2_SECRET is set.'
            ))
        app.sites.set([site])

        action = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(
            f'{action} Google SocialApp (client_id={client_id[:20]}...) for site {site.domain}'
        ))
        self.stdout.write(
            'Google redirect URI must include:\n'
            '  http://127.0.0.1:8000/accounts/google/login/callback/\n'
            'Open the app at http://127.0.0.1:8000/ (not localhost) to match this site.'
        )
