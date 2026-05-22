from django.contrib.auth.models import User
from django.db import models


class BusinessProfile(models.Model):
    """Profile for business users who offer services"""
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='business_profile')
    location = models.CharField(max_length=255, blank=True, default='')
    tel = models.CharField(max_length=50, blank=True, default='')
    description = models.TextField(blank=True, default='')
    working_hours = models.CharField(max_length=100, blank=True, default='')
    file = models.ImageField(
        upload_to='profile_pictures/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Business Profile: {self.user.username}"


class CustomerProfile(models.Model):
    """Profile for customers who order services"""
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='customer_profile')
    location = models.CharField(max_length=255, blank=True, default='')
    tel = models.CharField(max_length=50, blank=True, default='')
    description = models.TextField(blank=True, default='')
    working_hours = models.CharField(max_length=100, blank=True, default='')
    file = models.ImageField(
        upload_to='profile_pictures/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Customer Profile: {self.user.username}"
