from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from users.models import BusinessProfile, CustomerProfile


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    type = serializers.ChoiceField(
        choices=['business', 'customer'],
        write_only=True,
        required=True
    )
    token = serializers.CharField(read_only=True)
    user_id = serializers.IntegerField(source='id', read_only=True)
    
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'password', 'type', 'token']
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'username': {'required': True},
            'email': {'required': False}
        }
    
    def create(self, validated_data):
        """Create user, profile, and token"""
        profile_type = validated_data.pop('type')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        
        if profile_type == 'business':
            BusinessProfile.objects.create(user=user)
        else:
            CustomerProfile.objects.create(user=user)
        
        token = Token.objects.create(user=user)
        
        user.token = token.key
        user.type = profile_type
        
        return user
    
    def to_representation(self, instance):
        """Customize response format"""
        return {
            'token': instance.token,
            'user_id': instance.id,
            'username': instance.username,
            'email': instance.email,
            'type': instance.type
        }

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError('Invalid credentials')
        
        token, created = Token.objects.get_or_create(user=user)
        
        user_type = 'business' if hasattr(user, 'business_profile') else 'customer'

        return {
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'type': user_type
        }

class ProfileSerializer(serializers.Serializer):
    """Serializer for BusinessProfile and CustomerProfile"""
    user = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', required=False)
    first_name = serializers.CharField(source='user.first_name', required=False, allow_blank=True)
    last_name = serializers.CharField(source='user.last_name', required=False, allow_blank=True)
    
    location = serializers.CharField(required=False, allow_blank=True)
    tel = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    working_hours = serializers.CharField(required=False, allow_blank=True)
    file = serializers.ImageField(required=False, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True)
    
    type = serializers.SerializerMethodField()
    
    def get_type(self, obj):
        """Determine if this is a business or customer profile"""
        return 'business' if isinstance(obj, BusinessProfile) else 'customer'

    def update(self, instance, validated_data):
        """Update both User and Profile fields"""
        user_data = validated_data.pop('user', {})
        
        if user_data:
            for key, value in user_data.items():
                setattr(instance.user, key, value)
            instance.user.save()
        
        if validated_data:
            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save()
        
        return instance

    def to_representation(self, instance):
        """Convert None to empty string for text fields"""
        data = super().to_representation(instance)
        
        data['first_name'] = data.get('first_name') or ''
        data['last_name'] = data.get('last_name') or ''
        data['location'] = data.get('location') or ''
        data['tel'] = data.get('tel') or ''
        data['description'] = data.get('description') or ''
        data['working_hours'] = data.get('working_hours') or ''
        
        return data