from django.db import models
from django.conf import settings


class Achievement(models.Model):
    """
    Modelo para representar conquistas do usuário.
    """
    ACHIEVEMENT_TYPES = [
        ('streak', 'Streak'),
        ('cards', 'Cards'),
        ('accuracy', 'Accuracy'),
        ('level', 'Level'),
        ('time', 'Time'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(max_length=100, choices=ACHIEVEMENT_TYPES)
    name = models.CharField(max_length=100)
    description = models.TextField()
    unlocked_at = models.DateTimeField(auto_now_add=True)
    icon = models.CharField(max_length=50, default='trophy')
    points = models.IntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['type'])
        ]
        ordering = ['-unlocked_at']
        unique_together = ['user', 'type', 'name']

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class AchievementDefinition(models.Model):
    """
    Modelo para definir as conquistas disponíveis.
    """
    type = models.CharField(max_length=100, choices=Achievement.ACHIEVEMENT_TYPES)
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='trophy')
    points = models.IntegerField(default=0)
    requirement_value = models.IntegerField()
    requirement_type = models.CharField(max_length=100)

    class Meta:
        ordering = ['type', 'requirement_value']

    def __str__(self):
        return self.name

    def check_achievement(self, user):
        """
        Verifica se o usuário alcançou a conquista.
        """
        from apps.progress.models import UserProgress
        progress = UserProgress.objects.get(user=user)

        achieved = False
        if self.type == 'streak':
            achieved = progress.current_streak >= self.requirement_value
        elif self.type == 'cards':
            achieved = progress.total_cards >= self.requirement_value
        elif self.type == 'accuracy':
            achieved = progress.accuracy_rate >= self.requirement_value
        elif self.type == 'level':
            level_values = {'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5, 'C2': 6}
            achieved = level_values.get(progress.current_level, 0) >= self.requirement_value
        elif self.type == 'time':
            achieved = progress.time_spent >= self.requirement_value

        if achieved:
            Achievement.objects.get_or_create(
                user=user,
                type=self.type,
                name=self.name,
                defaults={
                    'description': self.description,
                    'icon': self.icon,
                    'points': self.points
                }
            ) 