from django.urls import path, include
from rest_framework.routers import DefaultRouter

from ..views import AchievementViewSet, AchievementDefinitionViewSet

router = DefaultRouter()
router.register('', AchievementViewSet, basename='achievement')
router.register('definitions', AchievementDefinitionViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 