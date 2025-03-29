"""
Production settings.
"""

import os
import sys
import logging
import dj_database_url
from .base import *  # noqa

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 31536000
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')

# Sentry - Configuração opcional
try:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration

    sentry_sdk.init(
        dsn=os.environ.get('SENTRY_DSN'),
        integrations=[
            DjangoIntegration(),
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR,
            ),
        ],
        traces_sample_rate=float(os.environ.get('SENTRY_TRACES_SAMPLE_RATE', '0.1')),
        send_default_pii=True,
        environment=os.environ.get('ENVIRONMENT', 'production'),
    )
    print("Sentry inicializado com sucesso.", file=sys.stderr)
except ImportError:
    print("AVISO: Módulo sentry_sdk não encontrado. O monitoramento de erros com Sentry está desativado.", file=sys.stderr)

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/var/log/fala_facil/app.log',
            'level': 'WARNING',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'mail_admins': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# Database configuration for Railway
# Verificar se DATABASE_URL está definido no ambiente
DATABASE_URL = os.environ.get('DATABASE_URL')

# Configuração do banco de dados com fallback mais robusto
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600)
    }
    # Garantir que o ENGINE está definido
    if 'ENGINE' not in DATABASES['default']:
        import sys
        print("ERRO: DATABASE_URL não contém ENGINE válido", file=sys.stderr)
        print(f"DATABASE_URL: {DATABASE_URL}", file=sys.stderr)
        # Fallback para PostgreSQL
        DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql'
else:
    # Fallback para SQLite se DATABASE_URL não estiver definido
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    print("AVISO: Usando SQLite como fallback. DATABASE_URL não está definido.", file=sys.stderr)