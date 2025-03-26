from rest_framework import serializers
from .models import UserProgress


class UserProgressSerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo UserProgress.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProgress
        fields = (
            'id', 'username', 'email', 'current_level', 'total_cards',
            'mastered_cards', 'current_streak', 'longest_streak',
            'accuracy_rate', 'average_response_time', 'cards_per_day',
            'time_spent', 'last_study_date', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'username', 'email', 'total_cards', 'mastered_cards',
            'current_streak', 'longest_streak', 'accuracy_rate',
            'average_response_time', 'cards_per_day', 'time_spent',
            'last_study_date', 'created_at', 'updated_at'
        ) 