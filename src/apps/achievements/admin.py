"""
from django.contrib import admin
from .models import Achievement, AchievementDefinition


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'name', 'points', 'unlocked_at')
    list_filter = ('type',)
    search_fields = ('user__username', 'name', 'description')
    ordering = ('-unlocked_at',)


@admin.register(AchievementDefinition)
class AchievementDefinitionAdmin(admin.ModelAdmin):
    list_display = ('type', 'name', 'points', 'requirement_value', 'requirement_type')
    list_filter = ('type',)
    search_fields = ('name', 'description')
    ordering = ('type', 'requirement_value')
""" 