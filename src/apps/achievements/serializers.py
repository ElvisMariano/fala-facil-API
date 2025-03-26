from rest_framework import serializers
from .models import Achievement, AchievementDefinition


class AchievementSerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo Achievement.
    """
    class Meta:
        model = Achievement
        fields = ('id', 'type', 'name', 'description', 'unlocked_at', 'icon', 'points')
        read_only_fields = ('id', 'unlocked_at')


class AchievementDefinitionSerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo AchievementDefinition.
    """
    is_achieved = serializers.SerializerMethodField()

    class Meta:
        model = AchievementDefinition
        fields = ('id', 'type', 'name', 'description', 'icon', 'points',
                 'requirement_value', 'requirement_type', 'is_achieved')
        read_only_fields = ('id',)

    def get_is_achieved(self, obj):
        """
        Verifica se o usuário atual já alcançou esta conquista.
        """
        user = self.context['request'].user
        return Achievement.objects.filter(
            user=user,
            type=obj.type,
            name=obj.name
        ).exists()


class AchievementStatsSerializer(serializers.Serializer):
    """
    Serializador para estatísticas de conquistas.
    """
    total_achievements = serializers.IntegerField()
    total_points = serializers.IntegerField()
    achievements_by_type = serializers.DictField(
        child=serializers.IntegerField()
    )
    recent_achievements = AchievementSerializer(many=True) 