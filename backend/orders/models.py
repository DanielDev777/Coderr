from django.contrib.auth.models import User
from django.db import models

from offers.models import OfferDetail


class Order(models.Model):
    """Order created by customer from an OfferDetail."""

    customer_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders_as_customer'
    )
    business_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders_as_business'
    )
    offer_detail = models.ForeignKey(
        OfferDetail,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )

    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(
        max_length=20,
        choices=[
            ('basic', 'Basic'),
            ('standard', 'Standard'),
            ('premium', 'Premium')
        ]
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled')
        ],
        default='in_progress'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.title} ({self.status})"
    
    class Meta:
        ordering = ['-created_at']