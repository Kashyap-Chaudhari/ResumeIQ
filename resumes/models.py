from django.db import models
from django.contrib.auth.models import User

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=255, default='My Resume')
    file = models.FileField(upload_to='resumes/')
    raw_text = models.TextField(blank=True, default='')
    parsed_skills = models.JSONField(default=list, blank=True)
    parsed_sections = models.JSONField(default=dict, blank=True) # experience, education, projects, contact
    ats_score = models.IntegerField(default=0) # 0-100
    ats_breakdown = models.JSONField(default=dict, blank=True) # formatting, keywords, impact, verbs, completeness
    ats_feedback = models.JSONField(default=list, blank=True)
    ai_analysis = models.JSONField(default=dict, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username} (Score: {self.ats_score})"

    def save(self, *args, **kwargs):
        if self.is_primary:
            # Set other resumes of this user to not primary
            Resume.objects.filter(user=self.user).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)
