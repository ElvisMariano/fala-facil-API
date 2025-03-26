"""
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import UserProgressViewSet

router = DefaultRouter()
router.register('', UserProgressViewSet, basename='progress')

urlpatterns = router.urls
""" 