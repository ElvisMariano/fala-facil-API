from django.urls import path, include
from rest_framework.routers import DefaultRouter

from ..views import UserProgressViewSet

router = DefaultRouter()
router.register('', UserProgressViewSet, basename='progress')

urlpatterns = [
    path('', include(router.urls)),
] 