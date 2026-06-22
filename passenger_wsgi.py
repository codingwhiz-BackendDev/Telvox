import sys, os

sys.path.insert(0, '/home/diggy/aidigpay.com')
os.environ['DJANGO_SETTINGS_MODULE'] = 'Telvox.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()