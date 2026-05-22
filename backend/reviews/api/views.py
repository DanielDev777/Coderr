from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from offers.models import Offer
from reviews.models import Review
from reviews.api.serializers import (
    ReviewSerializer,
    ReviewCreateSerializer,
    ReviewUpdateSerializer
)
from reviews.permissions import IsCustomerUser, IsReviewOwner
from users.models import BusinessProfile

class ReviewListView(ListCreateAPIView):
    """API endpoint for listing and creating reviews."""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['business_user_id', 'reviewer_id']
    ordering_fields = ['updated_at', 'rating']
    ordering = ['-updated_at']
    pagination_class = None

    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.request.method == 'POST':
            return ReviewCreateSerializer
        return ReviewSerializer
    
    def get_permissions(self):
        """Different permissions for different actions"""
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCustomerUser()]
        return [IsAuthenticated()]

class ReviewDetailView(RetrieveUpdateDestroyAPIView):
    """API endpoint for retrieving, updating, and deleting specific review."""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    
    def get_serializer_class(self):
        """Use update serializer for PATCH"""
        if self.request.method == 'PATCH':
            return ReviewUpdateSerializer
        return ReviewSerializer
    
    def get_permissions(self):
        """Different permissions for different actions"""
        if self.request.method == 'PATCH':
            return [IsAuthenticated(), IsReviewOwner()]
        elif self.request.method == 'DELETE':
            return [IsAuthenticated(), IsReviewOwner()]
        return [IsAuthenticated()]
    
class BaseInfoView(APIView):
    """API endpoint for platform-wide statistics."""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Return platform-wide statistics"""
        review_count = Review.objects.count()
        
        avg_rating = Review.objects.aggregate(Avg('rating'))['rating__avg'] or 0.0
        
        business_profile_count = BusinessProfile.objects.count()
        
        offer_count = Offer.objects.count()
        
        return Response({
            'review_count': review_count,
            'average_rating': round(avg_rating, 1),
            'business_profile_count': business_profile_count,
            'offer_count': offer_count
        }, status=status.HTTP_200_OK)