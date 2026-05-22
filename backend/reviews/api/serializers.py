from django.contrib.auth.models import User
from rest_framework import serializers

from reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model matching specification exactly."""

    class Meta:
        model = Review
        fields = [
            'id', 'business_user', 'reviewer', 'rating', 'description',
            'created_at', 'updated_at'
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
        """Validate user is not reviewing themselves and no duplicate exists"""
        request = self.context.get('request')
        
        if data['business_user'] == request.user:
            raise serializers.ValidationError({
                'business_user': "You cannot review yourself."
            })
        
        if Review.objects.filter(
            reviewer=request.user,
            business_user=data['business_user']
        ).exists():
            raise serializers.ValidationError(
                "You have already reviewed this business user."
            )
        
        return data
    
    def create(self, validated_data):
        """Create review with reviewer set from request.user"""
        validated_data['reviewer'] = self.context['request'].user
        return super().create(validated_data)
    
    def to_representation(self, instance):
        """Return full review representation after creation"""
        return ReviewSerializer(instance).data
    
class ReviewUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating reviews.
    
    Only allows updating rating and description
    """
    
    class Meta:
        model = Review
        fields = ['rating', 'description']
    
    def validate_description(self, value):
        """Validate description is not empty if provided"""
        if value is not None and (not value or not value.strip()):
            raise serializers.ValidationError(
                "Description cannot be empty."
            )
        return value
    
    def to_representation(self, instance):
        """Return full review representation after update"""
        return ReviewSerializer(instance).data