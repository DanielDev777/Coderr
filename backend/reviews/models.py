from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Review(models.Model):
    """Customer review for a business user."""

    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews_written'
    )
    business_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews_received'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['reviewer', 'business_user']
        ordering = ['-created_at'] 

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.business_user.username} ({self.rating}★)"
