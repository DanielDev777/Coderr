from rest_framework import serializers
from reviews.models import Review
from django.contrib.auth.models import User


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model (read-only for list)"""

    reviewer_username = serializers.CharField(
        source='reviewer.username', read_only=True)
    reviewer_first_name = serializers.CharField(
        source='reviewer.first_name', read_only=True)
    reviewer_last_name = serializers.CharField(
        source='reviewer.last_name', read_only=True)
    business_user_username = serializers.CharField(
        source='business_user.username', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'reviewer', 'business_user', 'rating', 'description',
            'created_at', 'updated_at',
            'reviewer_username', 'reviewer_first_name', 'reviewer_last_name',
            'business_user_username'
        ]
        read_only_fields = fields