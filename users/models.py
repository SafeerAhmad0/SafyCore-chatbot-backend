"""
User models and utilities for Supabase authentication
"""
from django.db import models


class UserProfile(models.Model):
    """
    Extended user profile stored in Django DB
    Links to Supabase user via user_id
    """
    user_id = models.CharField(max_length=255, unique=True, db_index=True)  # Supabase user UUID
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # User preferences
    default_session_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'user_profiles'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.email} ({self.user_id})"
