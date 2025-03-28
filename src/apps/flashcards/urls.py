"""URLs for flashcards app."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DeckFavoriteViewSet, DeckViewSet, FlashcardViewSet

app_name = 'flashcards'

router = DefaultRouter()
router.register('decks', DeckViewSet, basename='deck')
router.register('favorites', DeckFavoriteViewSet, basename='favorite')
router.register('flashcards', FlashcardViewSet, basename='flashcard')

urlpatterns = [
    path('', include(router.urls)),
] 