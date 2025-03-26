from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum
from django.utils import timezone

from .models import Achievement, AchievementDefinition
from .serializers import (
    AchievementSerializer,
    AchievementDefinitionSerializer,
    AchievementStatsSerializer
)


class AchievementViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar conquistas.
    """
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Achievement.objects.none()
        return Achievement.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False)
    def stats(self, request):
        """
        Retorna estatísticas das conquistas do usuário.
        """
        achievements = self.get_queryset()
        
        # Calcula estatísticas
        stats = {
            'total_achievements': achievements.count(),
            'total_points': achievements.aggregate(Sum('points'))['points__sum'] or 0,
            'achievements_by_type': dict(achievements.values('type').annotate(
                count=Count('id')
            ).values_list('type', 'count')),
            'recent_achievements': achievements.order_by('-unlocked_at')[:5]
        }

        serializer = AchievementStatsSerializer(stats)
        return Response(serializer.data)

    @action(detail=False)
    def check(self, request):
        """
        Verifica e atualiza as conquistas do usuário.
        """
        definitions = AchievementDefinition.objects.all()
        for definition in definitions:
            definition.check_achievement(request.user)
        
        return Response({'status': 'Achievements checked successfully'})


class AchievementDefinitionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para gerenciar definições de conquistas.
    """
    queryset = AchievementDefinition.objects.all()
    serializer_class = AchievementDefinitionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if not getattr(self, 'swagger_fake_view', False):
            context['user'] = self.request.user
        return context 