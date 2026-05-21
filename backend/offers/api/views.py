from rest_framework import filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Min

from offers.filters import OfferFilter
from offers.permissions import IsBusinessUser, IsOfferOwner
from offers.models import Offer, OfferDetail
from .serializers import OfferDetailSerializer, OfferListSerializer, OfferCreateSerializer, OfferUpdateSerializer


class OfferListView(ListCreateAPIView):
    """API endpoint for listing and creating offers."""
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OfferCreateSerializer
        return OfferListSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsBusinessUser()]
        return [AllowAny()]

    def perform_create(self, serializer):
        """Set the offer creator to the authenticated user."""
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = Offer.objects.select_related(
            'user').prefetch_related('details')

        queryset = queryset.annotate(
            min_price=Min('details__price'),
            min_delivery_time=Min('details__delivery_time_in_days')
        )

        return queryset

class OfferDetailView(RetrieveUpdateDestroyAPIView):
    """API endpoint for retrieving, updating, and deleting a single offer."""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Offer.objects.select_related('user').prefetch_related('details').annotate(
            min_price=Min('details__price'),
            min_delivery_time=Min('details__delivery_time_in_days')
        )
    
    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return OfferUpdateSerializer
        return OfferListSerializer
    
    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAuthenticated(), IsOfferOwner()]
        return [IsAuthenticated()]
    
class OfferTierDetailView(RetrieveAPIView):
    """API endpoint for retrieving a single offer pricing tier."""
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]