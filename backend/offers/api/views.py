from rest_framework import filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Min

from offers.filters import OfferFilter
from offers.permissions import IsBusinessUser
from offers.models import Offer
from .serializers import OfferListSerializer, OfferCreateSerializer


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
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = Offer.objects.select_related(
            'user').prefetch_related('details')

        queryset = queryset.annotate(
            min_price=Min('details__price'),
            min_delivery_time=Min('details__delivery_time_in_days')
        )

        return queryset

class OfferDetailView(RetrieveAPIView):
    """API endpoint for retrieving a single offer."""
    serializer_class = OfferListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Offer.objects.select_related('user').prefetch_related('details').annotate(
            min_price=Min('details__price'),
            min_delivery_time=Min('details__delivery_time_in_days')
        )
    