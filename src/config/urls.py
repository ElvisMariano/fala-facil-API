"""
URL configuration for fala-facil-api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from core.utils import CustomSchemaAPIView


def redirect_to_docs(request):
    return redirect('swagger-ui')


# API URLs
api_v1_patterns = [
    path('auth/', include('apps.users.urls.auth')),
    path('users/', include('apps.users.urls.users')),
    path('flashcards/', include('apps.flashcards.urls')),
    path('progress/', include('apps.progress.urls')),
    path('achievements/', include('apps.achievements.urls')),
]

urlpatterns = [
    path('', redirect_to_docs),
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='admin/login.html'), name='login'),
    path('api/v1/', include(api_v1_patterns)),
    path('api/schema/', CustomSchemaAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/', include('core.urls')),  # Incluindo as URLs do core, que contém o endpoint de saúde
]

# Debug toolbar
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
