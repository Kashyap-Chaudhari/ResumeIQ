from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    THEME_CHOICES = (
        ('dark', 'Dark Theme'),
        ('light', 'Light Theme'),
    )

    EXPERIENCE_CHOICES = (
        ('Entry', 'Entry Level (0-2 yrs)'),
        ('Mid', 'Mid Level (2-5 yrs)'),
        ('Senior', 'Senior Level (5-8 yrs)'),
        ('Lead', 'Lead / Staff (8+ yrs)'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    target_role = models.CharField(max_length=100, default='Full Stack Engineer', help_text='Target Career Role')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='Mid')
    gemini_api_key = models.CharField(max_length=255, blank=True, null=True, help_text='Optional custom Google Gemini API Key')
    theme_preference = models.CharField(max_length=10, choices=THEME_CHOICES, default='dark')
    bio = models.TextField(blank=True, default='')
    location = models.CharField(max_length=100, blank=True, default='')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile ({self.target_role})"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
