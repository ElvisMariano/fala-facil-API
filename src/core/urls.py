"""
Core URLs configuration.
"""

from django.urls import path
from .health import health_check

urlpatterns = [
    path('health/', health_check, name='health_check'),
] 