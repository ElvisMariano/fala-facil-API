"""Serializers for flashcards app."""

from rest_framework import serializers
from .models import Flashcard, FlashcardProgress, Deck


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

    def get_audio_url(self, obj):
        """Get audio URL."""
        return obj.get_audio_url()

    def get_image_url(self, obj):
        """Get image URL."""
        return obj.get_image_url()


class DeckSerializer(serializers.ModelSerializer):
    """Serializer for Deck model."""

    flashcards_count = serializers.SerializerMethodField()
    owner_username = serializers.SerializerMethodField()

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
            'is_public',
            'owner',
            'owner_username',
            'flashcards_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'owner',
            'created_at',
            'updated_at',
        ]

    def get_flashcards_count(self, obj):
        """Get number of flashcards in deck."""
        return obj.flashcards.count()

    def get_owner_username(self, obj):
        """Get owner username."""
        return obj.owner.username

    def create(self, validated_data):
        """Create deck with owner."""
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class DeckDetailSerializer(DeckSerializer):
    """Serializer for Deck model with flashcards."""

    flashcards = FlashcardSerializer(many=True, read_only=True)


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

    def get_accuracy_rate(self, obj):
        """
        Calcula a taxa de acerto para o flashcard.
        """
        total_attempts = obj.correct_attempts + obj.incorrect_attempts
        if total_attempts == 0:
            return 0
        return round((obj.correct_attempts / total_attempts) * 100, 2)


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