from django.db import models
import uuid

class TestSession(models.Model):
    """
    Represents a complete test session for a subject
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    started_at = models.DateTimeField(auto_now_add=True)
    current_sequence = models.IntegerField(default=1)
    current_state = models.CharField(max_length=1, choices=[
        ('R', 'Resting'),
        ('B', 'Bored'),
        ('F', 'Flow'),
        ('O', 'Overload')
    ])
    
    def __str__(self):
        return f"Session {self.id} - Sequence {self.current_sequence}"

class StateAttempt(models.Model):
    """
    Tracks individual attempts in each state
    """
    session = models.ForeignKey(TestSession, on_delete=models.CASCADE)
    state = models.CharField(max_length=1, choices=[
        ('R', 'Resting'),
        ('B', 'Bored'),
        ('F', 'Flow'),
        ('O', 'Overload')
    ])
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    difficulty_level = models.IntegerField(default=1)

class QuestionAttempt(models.Model):
    """
    Tracks individual question attempts within a state
    """
    state_attempt = models.ForeignKey(StateAttempt, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.CharField(max_length=100)
    correct_answer = models.CharField(max_length=100)
    is_correct = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
