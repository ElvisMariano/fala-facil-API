"""Serializers for flashcards app."""

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Flashcard, FlashcardProgress, Deck, DeckFavorite


class FlashcardSerializer(serializers.ModelSerializer):
    """Serializer for Flashcard model."""

    audio_url = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        """Meta options."""

        model = Flashcard
        fields = [
            'id',
            'deck',
            'front',
            'back',
            'example',
            'audio',
            'audio_url',
            'image',
            'image_url',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
        ]

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_audio_url(self, obj: Flashcard) -> str | None:
        """Get audio URL."""
        return obj.get_audio_url()

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_image_url(self, obj: Flashcard) -> str | None:
        """Get image URL."""
        return obj.get_image_url()


class DeckSerializer(serializers.ModelSerializer):
    """Serializer for Deck model."""

    is_favorite = serializers.SerializerMethodField()
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    parent_deck_name = serializers.CharField(source='parent_deck.name', read_only=True)

    class Meta:
        """Meta options."""

        model = Deck
        fields = [
            'id',
            'name',
            'description',
            'language',
            'level',
            'category',
            'owner',
            'owner_username',
            'is_public',
            'is_featured',
            'is_archived',
            'tags',
            'difficulty',
            'total_cards',
            'mastered_cards',
            'average_mastery_time',
            'study_count',
            'favorite_count',
            'share_count',
            'is_favorite',
            'color',
            'icon',
            'due_cards',
            'last_studied_at',
            'completion_rate',
            'version',
            'parent_deck',
            'parent_deck_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'owner',
            'owner_username',
            'is_featured',
            'difficulty',
            'total_cards',
            'mastered_cards',
            'average_mastery_time',
            'study_count',
            'favorite_count',
            'share_count',
            'is_favorite',
            'due_cards',
            'completion_rate',
            'parent_deck',
            'parent_deck_name',
            'created_at',
            'updated_at',
        ]

    @extend_schema_field(serializers.BooleanField())
    def get_is_favorite(self, obj: Deck) -> bool:
        """Return whether the deck is favorited by the current user."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return DeckFavorite.objects.filter(
                user=request.user,
                deck=obj,
            ).exists()
        return False

    def validate_name(self, value):
        """Validate name field."""
        if len(value) < 3:
            raise serializers.ValidationError(
                _('O nome deve ter pelo menos 3 caracteres.'),
            )
        return value

    def validate_color(self, value):
        """Validate color field."""
        if not value.startswith('#') or len(value) != 7:
            raise serializers.ValidationError(
                _('A cor deve estar no formato hexadecimal (#RRGGBB).'),
            )
        try:
            int(value[1:], 16)
        except ValueError:
            raise serializers.ValidationError(
                _('A cor deve estar no formato hexadecimal válido.'),
            )
        return value

    def validate_version(self, value):
        """Validate version field."""
        try:
            major, minor, patch = map(int, value.split('.'))
            if major < 0 or minor < 0 or patch < 0:
                raise ValueError
        except (ValueError, TypeError):
            raise serializers.ValidationError(
                _('A versão deve estar no formato semântico (x.y.z).'),
            )
        return value

    def validate(self, attrs):
        """Validate data."""
        # Verifica se o usuário está tentando arquivar um deck que não é seu
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if 'is_archived' in attrs and attrs['is_archived']:
                if self.instance and self.instance.owner != request.user:
                    raise serializers.ValidationError({
                        'is_archived': _('Você não pode arquivar um deck que não é seu.'),
                    })
        return attrs

    def create(self, validated_data):
        """Create a new deck."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['owner'] = request.user
        return super().create(validated_data)


class DeckDetailSerializer(DeckSerializer):
    """Serializer for Deck model with flashcards."""

    flashcards = FlashcardSerializer(many=True, read_only=True)

    class Meta(DeckSerializer.Meta):
        """Meta options."""

        fields = DeckSerializer.Meta.fields + ['flashcards']


class DeckFavoriteSerializer(serializers.ModelSerializer):
    """Serializer for DeckFavorite model."""

    deck = DeckSerializer(read_only=True)
    deck_id = serializers.PrimaryKeyRelatedField(
        queryset=Deck.objects.all(),
        write_only=True,
    )

    class Meta:
        """Meta options."""

        model = DeckFavorite
        fields = [
            'id',
            'user',
            'deck',
            'deck_id',
            'created_at',
        ]
        read_only_fields = [
            'user',
            'created_at',
        ]

    def validate_deck_id(self, value):
        """Validate deck_id field."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if DeckFavorite.objects.filter(
                user=request.user,
                deck=value,
            ).exists():
                raise serializers.ValidationError(
                    _('Este deck já está nos seus favoritos.'),
                )
        return value

    def create(self, validated_data):
        """Create a new deck favorite."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
            validated_data['deck'] = validated_data.pop('deck_id')
        return super().create(validated_data)


class FlashcardProgressSerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo FlashcardProgress.
    """
    flashcard = FlashcardSerializer(read_only=True)
    accuracy_rate = serializers.SerializerMethodField()

    class Meta:
        model = FlashcardProgress
        fields = (
            'id', 'flashcard', 'correct_attempts', 'incorrect_attempts',
            'average_response_time', 'last_reviewed', 'next_review_date',
            'ease_factor', 'interval', 'streak', 'accuracy_rate'
        )
        read_only_fields = (
            'id', 'correct_attempts', 'incorrect_attempts', 'average_response_time',
            'last_reviewed', 'next_review_date', 'ease_factor', 'interval',
            'streak', 'accuracy_rate'
        )

    @extend_schema_field(serializers.FloatField())
    def get_accuracy_rate(self, obj: FlashcardProgress) -> float:
        """Calculate accuracy rate."""
        total_attempts = obj.correct_attempts + obj.incorrect_attempts
        if total_attempts == 0:
            return 0.0
        return round(obj.correct_attempts / total_attempts * 100, 2)


class FlashcardReviewSerializer(serializers.Serializer):
    """
    Serializador para revisão de flashcard.
    """
    quality = serializers.IntegerField(min_value=0, max_value=5)
    response_time = serializers.FloatField(min_value=0)

    def validate_quality(self, value):
        """
        Valida a qualidade da resposta.
        """
        if not isinstance(value, int):
            raise serializers.ValidationError("A qualidade deve ser um número inteiro.")
        if value < 0 or value > 5:
            raise serializers.ValidationError("A qualidade deve estar entre 0 e 5.")
        return value

    def validate_response_time(self, value):
        """
        Valida o tempo de resposta.
        """
        if value < 0:
            raise serializers.ValidationError("O tempo de resposta não pode ser negativo.")
        return value 