from django.db import models
from django.contrib.auth.models import User
from resumes.models import Resume

class JobDescription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_descriptions')
    title = models.CharField(max_length=255, default='Target Job Role')
    company_name = models.CharField(max_length=255, blank=True, default='')
    raw_text = models.TextField()
    extracted_skills = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} at {self.company_name or 'Company'}"

class MatchAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='match_analyses')
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='matches')
    job_description = models.ForeignKey(JobDescription, on_delete=models.CASCADE, related_name='matches')
    match_score = models.FloatField(default=0.0) # 0.0 to 100.0
    matching_skills = models.JSONField(default=list, blank=True)
    missing_skills = models.JSONField(default=list, blank=True)
    skill_gap_summary = models.TextField(blank=True, default='')
    improvement_tips = models.JSONField(default=list, blank=True)
    ai_bullets = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Match: {self.resume.title} vs {self.job_description.title} ({self.match_score:.1f}%)"

class JobApplication(models.Model):
    STATUS_CHOICES = (
        ('Applied', 'Applied'),
        ('Under Review', 'Under Review'),
        ('Online Assessment', 'Online Assessment'),
        ('Technical Interview', 'Technical Interview'),
        ('HR Interview', 'HR Interview'),
        ('Final Interview', 'Final Interview'),
        ('Offer Received', 'Offer Received'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
        ('Withdrawn', 'Withdrawn'),
    )

    JOB_TYPE_CHOICES = (
        ('Full-Time', 'Full-Time'),
        ('Internship', 'Internship'),
        ('Part-Time', 'Part-Time'),
        ('Remote', 'Remote'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    company_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES, default='Full-Time')
    location = models.CharField(max_length=255, blank=True, default='')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Applied')
    match_analysis = models.ForeignKey(MatchAnalysis, on_delete=models.SET_NULL, null=True, blank=True, related_name='applications')
    salary = models.CharField(max_length=100, blank=True, default='')
    job_link = models.URLField(blank=True, default='')
    resume_version = models.CharField(max_length=255, blank=True, default='')
    cover_letter = models.CharField(max_length=255, blank=True, default='')
    notes = models.TextField(blank=True, default='')
    reminder_date = models.DateTimeField(null=True, blank=True)
    application_date = models.DateField(auto_now_add=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.job_title} @ {self.company_name} ({self.status})"

class LearningResource(models.Model):
    RESOURCE_TYPES = (
        ('Course', 'Free Online Course'),
        ('Documentation', 'Official Documentation'),
        ('Video', 'Video Tutorial'),
        ('Book', 'Book / Article'),
        ('Practice', 'Hands-on Practice Platform'),
    )

    skill_name = models.CharField(max_length=100, db_index=True)
    category = models.CharField(max_length=50, default='Technical')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    url = models.URLField()
    resource_type = models.CharField(max_length=50, choices=RESOURCE_TYPES, default='Course')
    is_free = models.BooleanField(default=True)
    provider = models.CharField(max_length=100, default='Free Resource')

    def __str__(self):
        return f"[{self.skill_name}] {self.title}"
