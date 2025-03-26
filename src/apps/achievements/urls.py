"""
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import AchievementViewSet, AchievementDefinitionViewSet

router = DefaultRouter()
router.register('', AchievementViewSet, basename='achievement')
router.register('definitions', AchievementDefinitionViewSet, basename='achievement-definition')

urlpatterns = router.urls
""" 