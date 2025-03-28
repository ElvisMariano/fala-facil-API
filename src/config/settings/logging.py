"""Logging configuration for the project."""

import os
from pathlib import Path

from django.conf import settings

# Ensure logs directory exists
LOGS_DIR = Path(settings.BASE_DIR) / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',  # Handler mais simples para desenvolvimento
            'filename': str(LOGS_DIR / 'fala_facil.log'),
            'formatter': 'verbose',
            'mode': 'a',  # Modo append
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],  # Removendo file handler para desenvolvimento
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins'],  # Removendo file handler para desenvolvimento
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['mail_admins'],  # Removendo file handler para desenvolvimento
            'level': 'ERROR',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],  # Removendo file handler para desenvolvimento
            'level': 'INFO',
            'propagate': True,
        },
    },
} 