"""
from django.contrib import admin
from .models import UserProgress


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_level', 'total_cards', 'mastered_cards', 'current_streak', 'accuracy_rate')
    list_filter = ('current_level',)
    search_fields = ('user__username',)
    ordering = ('-current_streak',)
""" 