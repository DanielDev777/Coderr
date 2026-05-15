from django.db import models
from django.contrib.auth.models import User


class Offer(models.Model):
    """Offer created by business users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="offers")
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='offer_images/', null=True, blank=True)
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def min_price(self):
        """Return the minimum price from all details"""
        prices = self.details.values_list('price', flat=True)
        return min(prices) if prices else None

    def min_delivery_time(self):
        """Return the minimum delivery time from all details"""
        times = self.details.values_list('delivery_time_in_days', flat=True)
        return min(times) if times else None

    def __str__(self):
        return f"{self.title} by {self.user.username}"


class OfferDetail(models.Model):
    """Details for offer tiers (basic, standard, premium)"""
    OFFER_TYPE_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]

    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="details")
    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=10, choices=OFFER_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.offer.title} - {self.offer_type}"
