from django.contrib import admin
from .models import TestSession, StateAttempt, QuestionAttempt

@admin.register(TestSession)
class TestSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'started_at', 'current_sequence', 'current_state')
    list_filter = ('current_sequence', 'current_state', 'started_at')

@admin.register(StateAttempt)
class StateAttemptAdmin(admin.ModelAdmin):
    list_display = ('session', 'state', 'start_time', 'end_time', 'difficulty_level')
    list_filter = ('state', 'difficulty_level')

@admin.register(QuestionAttempt)
class QuestionAttemptAdmin(admin.ModelAdmin):
    list_display = ('state_attempt', 'question', 'answer', 'correct_answer', 'is_correct', 'timestamp')
    list_filter = ('is_correct', 'timestamp')