"""
WSGI config for fala-facil-api project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Verificar se estamos no ambiente de produção (Railway)
if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RAILWAY_SERVICE_ID'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
