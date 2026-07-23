from django.db import models
from django.contrib.auth.models import User

class AIInterviewSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_interviews')
    role = models.CharField(max_length=150)
    experience = models.CharField(max_length=50, blank=True)
    skills = models.TextField(blank=True)
    difficulty = models.CharField(max_length=50, blank=True)
    type = models.CharField(max_length=50, blank=True)
    resume_text = models.TextField(blank=True)
    job_description = models.TextField(blank=True)
    
    status = models.CharField(max_length=50, default='active') # active, completed
    
    # Session summary stats
    total_questions = models.IntegerField(default=0)
    correct_responses = models.IntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    duration_seconds = models.IntegerField(default=0)
    
    # Final report
    final_report = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role} ({self.created_at.strftime('%Y-%m-%d')})"

class AIInterviewQA(models.Model):
    session = models.ForeignKey(AIInterviewSession, on_delete=models.CASCADE, related_name='qas')
    question_text = models.TextField()
    user_answer = models.TextField(blank=True)
    evaluation_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
