from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Count
from django.utils import timezone

from .models import UserProgress
from .serializers import UserProgressSerializer
from apps.flashcards.models import FlashcardProgress


class UserProgressViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para gerenciar o progresso do usuário.
    """
    serializer_class = UserProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return UserProgress.objects.none()
        return UserProgress.objects.filter(user=self.request.user)

    @action(detail=False)
    def stats(self, request):
        """
        Retorna estatísticas detalhadas do progresso do usuário.
        """
        progress = UserProgress.objects.get_or_create(user=request.user)[0]
        flashcard_progress = FlashcardProgress.objects.filter(user=request.user)

        # Calcula estatísticas dos flashcards
        stats = flashcard_progress.aggregate(
            total_reviews=Count('id'),
            avg_response_time=Avg('average_response_time'),
            total_correct=Count('id', filter={'correct_attempts__gt': 0}),
            total_incorrect=Count('id', filter={'incorrect_attempts__gt': 0})
        )

        # Atualiza o progresso do usuário
        if stats['total_reviews'] > 0:
            progress.update_stats(
                correct_attempts=stats['total_correct'],
                incorrect_attempts=stats['total_incorrect'],
                response_time=stats['avg_response_time'] or 0
            )

        # Atualiza o streak
        progress.update_streak()

        return Response({
            'user_progress': UserProgressSerializer(progress).data,
            'recent_activity': {
                'today_reviews': flashcard_progress.filter(
                    last_reviewed__date=timezone.now().date()
                ).count(),
                'week_reviews': flashcard_progress.filter(
                    last_reviewed__gte=timezone.now() - timezone.timedelta(days=7)
                ).count(),
                'month_reviews': flashcard_progress.filter(
                    last_reviewed__gte=timezone.now() - timezone.timedelta(days=30)
                ).count()
            },
            'level_distribution': self._get_level_distribution(flashcard_progress)
        })

    def _get_level_distribution(self, flashcard_progress):
        """
        Calcula a distribuição de níveis dos flashcards do usuário.
        """
        distribution = {}
        for progress in flashcard_progress.select_related('flashcard'):
            level = progress.flashcard.level
            if level not in distribution:
                distribution[level] = {
                    'total': 0,
                    'mastered': 0
                }
            distribution[level]['total'] += 1
            if progress.correct_attempts > 0 and progress.correct_attempts >= progress.incorrect_attempts * 2:
                distribution[level]['mastered'] += 1
        return distribution 