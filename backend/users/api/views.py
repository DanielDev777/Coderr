from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import RetrieveUpdateAPIView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import Http404

from .serializers import RegistrationSerializer, LoginSerializer, ProfileSerializer


class RegistrationView(APIView):
    """
    API endpoint for user registration.
    Creates a new user with either a business or customer profile.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """Handle user registration"""
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """Login user and return authentication token."""
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            return Response(
                serializer.validated_data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class ProfileDetailView(RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs.get('pk')
        user = get_object_or_404(User, id=user_id)

        # Check if user has business_profile
        if hasattr(user, 'business_profile'):
            return user.business_profile

        # Check if user has customer_profile
        if hasattr(user, 'customer_profile'):
            return user.customer_profile

        # If neither exists, raise 404
        raise Http404("Profile not found")