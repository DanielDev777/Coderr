from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from reviews.models import Review
from reviews.api.serializers import ReviewSerializer, ReviewCreateSerializer
from reviews.permissions import IsCustomerUser

class ReviewListView(ListCreateAPIView):
    """API endpoint for listing and creating reviews."""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['business_user_id', 'reviewer_id']
    ordering_fields = ['created_at', 'updated_at', 'rating']
    ordering = ['-updated_at']

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