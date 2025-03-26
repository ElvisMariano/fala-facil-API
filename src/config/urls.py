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
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


def redirect_to_docs(request):
    return redirect('schema-swagger-ui')


# Schema view for API documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Fala Fácil API",
        default_version='v1',
        description="API para o aplicativo Fala Fácil",
        terms_of_service="https://www.falafacil.com/terms/",
        contact=openapi.Contact(email="contato@falafacil.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

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
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Debug toolbar
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
