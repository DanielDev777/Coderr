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

class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating reviews."""
    
    class Meta:
        model = Review
        fields = ['business_user', 'rating', 'description']
    
    def validate_business_user(self, value):
        """Validate business_user exists and has BusinessProfile"""
        if not hasattr(value, 'business_profile'):
            raise serializers.ValidationError(
                "This user is not a business user."
            )
        return value
    
    def validate_description(self, value):
        """Validate description is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError(
                "Description cannot be empty."
            )
        return value
    
    def validate(self, data):
        """Validate user is not reviewing themselves"""
        request = self.context.get('request')
        if data['business_user'] == request.user:
            raise serializers.ValidationError({
                'business_user': "You cannot review yourself."
            })
        return data
    
    def create(self, validated_data):
        """Create review with reviewer set from request.user"""
        validated_data['reviewer'] = self.context['request'].user
        return super().create(validated_data)
    
    def to_representation(self, instance):
        """Return full review representation after creation"""
        return ReviewSerializer(instance).data