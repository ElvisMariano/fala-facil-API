"""
Test settings.
"""

from .base import *  # noqa

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'test-secret-key'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

# Use SQLite for tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Disable password hashing to speed up tests
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Email
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Media files
MEDIA_ROOT = BASE_DIR / "test_media"  # noqa F405

# Disable migrations
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Caching
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Celery
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Security
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Logging
LOGGING["handlers"]["console"]["level"] = "CRITICAL"  # noqa F405
LOGGING["handlers"]["file"]["level"] = "CRITICAL"  # noqa F405
for logger in LOGGING["loggers"].values():  # noqa F405
    logger["level"] = "CRITICAL"

# Disable debug toolbar
if 'debug_toolbar' in INSTALLED_APPS:  # noqa
    INSTALLED_APPS.remove('debug_toolbar')  # noqa
if 'debug_toolbar.middleware.DebugToolbarMiddleware' in MIDDLEWARE:  # noqa
    MIDDLEWARE.remove('debug_toolbar.middleware.DebugToolbarMiddleware')  # noqa 