"""
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import FlashcardViewSet, FlashcardProgressViewSet

router = DefaultRouter()
router.register('', FlashcardViewSet, basename='flashcard')
router.register('progress', FlashcardProgressViewSet, basename='flashcard-progress')

urlpatterns = router.urls
""" 