from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsOwnerOrReadOnly
from .serializers import (
    RegistrationSerializer, 
    LoginSerializer, 
    ProfileSerializer,
    BusinessProfileListSerializer,
    CustomerProfileListSerializer
)
from users.models import BusinessProfile, CustomerProfile


class RegistrationView(APIView):
    """
    API endpoint for user registration.
    Creates a new user with either a business or customer profile.
    """
    permission_classes = [AllowAny]

    def post(self, request):
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
    """API endpoint for user login and token generation."""
    permission_classes = [AllowAny]

    def post(self, request):
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
    """API endpoint for retrieving and updating user profiles."""
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self):
        """Get profile (business or customer) for the user."""
        user_id = self.kwargs.get('pk')
        user = get_object_or_404(User, id=user_id)

        if hasattr(user, 'business_profile'):
            profile = user.business_profile
        elif hasattr(user, 'customer_profile'):
            profile = user.customer_profile
        else:
            raise Http404("Profile not found")
        
        self.check_object_permissions(self.request, profile)
        return profile

class BusinessProfileListView(ListAPIView):
    """API endpoint for listing business profiles."""
    serializer_class = BusinessProfileListSerializer
    permission_classes = [IsAuthenticated]
    queryset = BusinessProfile.objects.all()
    pagination_class = None

class CustomerProfileListView(ListAPIView):
    """API endpoint for listing customer profiles."""
    serializer_class = CustomerProfileListSerializer
    permission_classes = [IsAuthenticated]
    queryset = CustomerProfile.objects.all()
    pagination_class = None