from django.db.models import Q
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from rest_framework import viewsets, permissions, status, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from .models import Flashcard, FlashcardProgress, Deck, DeckFavorite
from .serializers import (
    FlashcardSerializer,
    FlashcardProgressSerializer,
    FlashcardReviewSerializer,
    DeckDetailSerializer,
    DeckSerializer,
    DeckFavoriteSerializer,
)
from .services import DeckRecommendationService, DeckExportService, DeckImportService


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


@extend_schema(tags=['decks'])
class DeckViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de decks de flashcards.
    
    Permite criar, listar, atualizar e excluir decks, além de operações especiais
    como exportar, importar e obter recomendações.
    """

    queryset = Deck.objects.all()
    serializer_class = DeckSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['language', 'level', 'category', 'is_public', 'is_featured']
    search_fields = ['name', 'description', 'tags']
    ordering_fields = [
        'name',
        'created_at',
        'updated_at',
        'difficulty',
        'total_cards',
        'mastered_cards',
        'study_count',
        'favorite_count',
        'share_count',
    ]
    ordering = ['name']
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    @extend_schema(
        summary="Listar decks",
        description="Lista todos os decks públicos ou do usuário atual.",
        responses={200: DeckSerializer(many=True)},
        tags=['decks'],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Criar deck",
        description="Cria um novo deck de flashcards.",
        request=DeckSerializer,
        responses={201: DeckSerializer()},
        tags=['decks'],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Detalhes do deck",
        description="Retorna os detalhes de um deck específico.",
        responses={200: DeckDetailSerializer()},
        tags=['decks'],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Atualizar deck",
        description="Atualiza um deck existente.",
        request=DeckSerializer,
        responses={200: DeckSerializer()},
        tags=['decks'],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Atualizar deck parcialmente",
        description="Atualiza parcialmente um deck existente.",
        request=DeckSerializer,
        responses={200: DeckSerializer()},
        tags=['decks'],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Remover deck",
        description="Remove um deck.",
        responses={204: None},
        tags=['decks'],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        summary="Recomendações de decks",
        description="Retorna decks recomendados para o usuário atual.",
        responses={200: DeckSerializer(many=True)},
        tags=['decks'],
    )
    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """Return deck recommendations."""
        service = DeckRecommendationService(request.user)
        recommendations = service.get_recommendations()
        serializer = self.get_serializer(recommendations, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Exportar deck",
        description="Exporta um deck para JSON ou CSV.",
        parameters=[
            OpenApiParameter(
                name='format',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Formato de exportação (json ou csv)',
                required=False,
                default='json',
            ),
        ],
        responses={200: bytes},
        tags=['decks'],
    )
    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        """Export deck."""
        deck = self.get_object()
        format = request.query_params.get('format', 'json')

        try:
            service = DeckExportService(deck)
            content = service.export(format)

            # Define o tipo de conteúdo e nome do arquivo
            if format == 'json':
                content_type = 'application/json'
                filename = f'{deck.name}.json'
            else:
                content_type = 'text/csv'
                filename = f'{deck.name}.csv'

            response = Response(content, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except ValueError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @extend_schema(
        summary="Importar deck",
        description="Importa um deck de um arquivo JSON ou CSV.",
        request={'multipart/form-data': {'file': bytes}},
        responses={201: DeckSerializer()},
        tags=['decks'],
    )
    @action(detail=False, methods=['post'])
    def import_deck(self, request):
        """Import deck."""
        if 'file' not in request.FILES:
            return Response(
                {'detail': 'Nenhum arquivo foi enviado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        file = request.FILES['file']
        format = file.name.split('.')[-1].lower()

        try:
            service = DeckImportService(request.user)
            deck = service.import_deck(
                file.read(),
                format=format,
            )
            serializer = self.get_serializer(deck)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @extend_schema(
        summary="Meus decks",
        description="Lista todos os decks do usuário atual.",
        responses={200: DeckSerializer(many=True)},
        tags=['decks'],
    )
    @action(detail=False, methods=['get'])
    def my_decks(self, request):
        """Return user's decks."""
        queryset = self.get_queryset().filter(owner=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Decks públicos",
        description="Lista todos os decks públicos.",
        responses={200: DeckSerializer(many=True)},
        tags=['decks'],
    )
    @action(detail=False, methods=['get'])
    def public_decks(self, request):
        """Return public decks."""
        queryset = self.get_queryset().filter(is_public=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Decks em destaque",
        description="Lista todos os decks em destaque.",
        responses={200: DeckSerializer(many=True)},
        tags=['decks'],
    )
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Return featured decks."""
        queryset = self.get_queryset().filter(is_featured=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Decks arquivados",
        description="Lista todos os decks arquivados do usuário atual.",
        responses={200: DeckSerializer(many=True)},
        tags=['decks'],
    )
    @action(detail=False, methods=['get'])
    def archived(self, request):
        """Return archived decks."""
        queryset = self.get_queryset().filter(
            owner=request.user,
            is_archived=True,
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Duplicar deck",
        description="Cria uma cópia de um deck existente.",
        responses={201: DeckSerializer()},
        tags=['decks'],
    )
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a deck."""
        deck = self.get_object()
        new_deck = deck.duplicate(new_owner=request.user)
        serializer = self.get_serializer(new_deck)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Arquivar deck",
        description="Arquiva um deck.",
        responses={204: None},
        tags=['decks'],
    )
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a deck."""
        deck = self.get_object()
        if deck.owner != request.user:
            return Response(
                {'detail': _('Você não pode arquivar um deck que não é seu.')},
                status=status.HTTP_403_FORBIDDEN,
            )
        deck.archive()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Desarquivar deck",
        description="Desarquiva um deck.",
        responses={204: None},
        tags=['decks'],
    )
    @action(detail=True, methods=['post'])
    def unarchive(self, request, pk=None):
        """Unarchive a deck."""
        deck = self.get_object()
        if deck.owner != request.user:
            return Response(
                {'detail': _('Você não pode desarquivar um deck que não é seu.')},
                status=status.HTTP_403_FORBIDDEN,
            )
        deck.unarchive()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Compartilhar deck",
        description="Incrementa o contador de compartilhamentos do deck.",
        responses={204: None},
        tags=['decks'],
    )
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Share a deck."""
        deck = self.get_object()
        deck.increment_share_count()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['favorites'])
class DeckFavoriteViewSet(viewsets.ModelViewSet):
    """ViewSet for DeckFavorite model."""

    queryset = DeckFavorite.objects.all()
    serializer_class = DeckFavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['-created_at']

    @extend_schema(
        summary="Listar favoritos",
        description="Lista todos os decks favoritos do usuário atual.",
        responses={200: DeckFavoriteSerializer(many=True)},
        tags=['favorites'],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Adicionar aos favoritos",
        description="Adiciona um deck aos favoritos.",
        request=DeckFavoriteSerializer,
        responses={201: DeckFavoriteSerializer()},
        tags=['favorites'],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Remover dos favoritos",
        description="Remove um deck dos favoritos.",
        responses={204: None},
        tags=['favorites'],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        """Return queryset."""
        return self.queryset.filter(user=self.request.user)


@extend_schema(tags=['flashcards'])
class FlashcardViewSet(viewsets.ModelViewSet):
    """ViewSet for Flashcard model."""

    queryset = Flashcard.objects.all()
    serializer_class = FlashcardSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['deck']
    search_fields = ['front', 'back', 'example']
    ordering_fields = ['front', 'created_at', 'updated_at']
    ordering = ['front']

    def get_queryset(self):
        """Return queryset."""
        queryset = super().get_queryset()
        if self.action in ['list', 'retrieve']:
            # Filtra flashcards de decks públicos ou do usuário atual
            queryset = queryset.filter(
                Q(deck__is_public=True) | Q(deck__owner=self.request.user),
            )
        else:
            # Para outras ações, filtra apenas flashcards de decks do usuário
            queryset = queryset.filter(deck__owner=self.request.user)
        # Exclui flashcards de decks arquivados
        queryset = queryset.filter(deck__is_archived=False)
        return queryset

    @action(detail=False, methods=['get'])
    def my_flashcards(self, request):
        """Return user's flashcards."""
        queryset = self.get_queryset().filter(deck__owner=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def public_flashcards(self, request):
        """Return public flashcards."""
        queryset = self.get_queryset().filter(deck__is_public=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
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