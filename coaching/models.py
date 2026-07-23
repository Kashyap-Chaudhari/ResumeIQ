from django.db import models
from django.contrib.auth.models import User

class PlacementReadiness(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='readiness')
    overall_score = models.IntegerField(default=50) # 0-100
    domain_scores = models.JSONField(default=dict, blank=True) # technical, problem_solving, experience, resume_quality, interview_prep
    top_strengths = models.JSONField(default=list, blank=True)
    critical_gaps = models.JSONField(default=list, blank=True)
    recommendations = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Placement Readiness ({self.overall_score}/100)"

class InterviewSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interview_sessions')
    target_role = models.CharField(max_length=150, default='Software Engineer')
    company_name = models.CharField(max_length=150, blank=True, default='')
    questions_data = models.JSONField(default=list, blank=True) # list of Q&A objects
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Interview Prep for {self.target_role} ({self.created_at.strftime('%Y-%m-%d')})"

class CareerRoadmap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roadmaps')
    target_role = models.CharField(max_length=150, default='Software Engineer')
    current_level = models.CharField(max_length=50, default='Mid Level')
    milestones = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Roadmap for {self.target_role} ({self.created_at.strftime('%Y-%m-%d')})"
