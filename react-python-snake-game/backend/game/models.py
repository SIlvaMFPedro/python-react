from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class GameSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    score = models.IntegerField(default=0)
    moves = models.IntegerField(default=0)
    duration = models.IntegerField(default=0)   # in seconds
    ai_mode = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-score', '-created_at']

    def __str__(self):
        return f"Session {self.id} - Score: {self.score}"


class HighScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    username = models.CharField(max_length=100, default='Anonymous')
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-score']

    def __str__(self):
        return f"{self.username} - {self.score}"