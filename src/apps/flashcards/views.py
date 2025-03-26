from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters

from .models import Flashcard, FlashcardProgress, Deck
from .serializers import (
    FlashcardSerializer,
    FlashcardProgressSerializer,
    FlashcardReviewSerializer,
    DeckDetailSerializer,
    DeckSerializer,
)


class FlashcardFilter(filters.FilterSet):
    """
    Filtros para o modelo Flashcard.
    """
    level = filters.CharFilter(lookup_expr='exact')
    category = filters.CharFilter(lookup_expr='icontains')
    tags = filters.CharFilter(method='filter_tags')
    search = filters.CharFilter(method='filter_search')

    def filter_tags(self, queryset, name, value):
        tags = value.split(',')
        return queryset.filter(tags__contains=tags)

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(front__icontains=value) | Q(back__icontains=value))

    class Meta:
        model = Flashcard
        fields = ['level', 'category', 'tags']


class DeckViewSet(viewsets.ModelViewSet):
    """ViewSet for Deck model."""

    queryset = Deck.objects.all()
    serializer_class = DeckSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return decks that are public or owned by the user."""
        return Deck.objects.filter(
            Q(is_public=True) | Q(owner=self.request.user),
        )

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'retrieve':
            return DeckDetailSerializer
        return self.serializer_class

    @action(detail=False, methods=['get'])
    def my_decks(self, request):
        """Return decks owned by the user."""
        decks = Deck.objects.filter(owner=request.user)
        serializer = self.get_serializer(decks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def public_decks(self, request):
        """Return public decks."""
        decks = Deck.objects.filter(is_public=True)
        serializer = self.get_serializer(decks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def flashcards(self, request, pk=None):
        """Return flashcards in deck."""
        deck = self.get_object()
        flashcards = deck.flashcards.all()
        serializer = FlashcardSerializer(flashcards, many=True)
        return Response(serializer.data)


class FlashcardViewSet(viewsets.ModelViewSet):
    """ViewSet for Flashcard model."""

    queryset = Flashcard.objects.all()
    serializer_class = FlashcardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return flashcards from decks that are public or owned by the user."""
        return Flashcard.objects.filter(
            Q(deck__is_public=True) | Q(deck__owner=self.request.user),
        )

    @action(detail=False, methods=['get'])
    def my_flashcards(self, request):
        """Return flashcards from decks owned by the user."""
        flashcards = Flashcard.objects.filter(deck__owner=request.user)
        serializer = self.get_serializer(flashcards, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def public_flashcards(self, request):
        """Return flashcards from public decks."""
        flashcards = Flashcard.objects.filter(deck__is_public=True)
        serializer = self.get_serializer(flashcards, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """
        Endpoint para revisar um flashcard.
        """
        flashcard = self.get_object()
        serializer = FlashcardReviewSerializer(data=request.data)
        
        if serializer.is_valid():
            progress, created = FlashcardProgress.objects.get_or_create(
                user=request.user,
                flashcard=flashcard
            )

            # Atualiza o tempo médio de resposta
            if progress.average_response_time == 0:
                progress.average_response_time = serializer.validated_data['response_time']
            else:
                progress.average_response_time = (
                    progress.average_response_time + serializer.validated_data['response_time']
                ) / 2

            # Calcula a próxima revisão
            progress.calculate_next_review(serializer.validated_data['quality'])
            progress.save()

            return Response(FlashcardProgressSerializer(progress).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False)
    def due_review(self, request):
        """
        Retorna os flashcards que precisam ser revisados.
        """
        now = timezone.now()
        progress = FlashcardProgress.objects.filter(
            user=request.user,
            next_review_date__lte=now
        ).select_related('flashcard')

        # Se não houver cards para revisar, retorna novos cards
        if not progress.exists():
            reviewed_cards = FlashcardProgress.objects.filter(
                user=request.user
            ).values_list('flashcard_id', flat=True)
            
            new_cards = Flashcard.objects.exclude(
                id__in=reviewed_cards
            )[:10]
            
            return Response(FlashcardSerializer(new_cards, many=True).data)

        return Response(FlashcardProgressSerializer(progress, many=True).data)

    @action(detail=False)
    def progress(self, request):
        """
        Retorna o progresso do usuário em todos os flashcards.
        """
        progress = FlashcardProgress.objects.filter(
            user=request.user
        ).select_related('flashcard')
        
        return Response(FlashcardProgressSerializer(progress, many=True).data)


class FlashcardProgressViewSet(viewsets.ModelViewSet):
    serializer_class = FlashcardProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['flashcard__level', 'flashcard__category']
    search_fields = ['flashcard__front', 'flashcard__back']
    ordering_fields = ['next_review_date', 'streak', 'correct_attempts']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return FlashcardProgress.objects.none()
        return FlashcardProgress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user) 