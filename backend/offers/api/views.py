from rest_framework import status, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from django_filters.rest_framework import DjangoFilterBackend
from offers.filters import OfferFilter
from django.db.models import Min

from offers.models import Offer
from .serializers import OfferListSerializer, OfferDetailListSerializer

class OfferListView(ListAPIView):
    serializer_class = OfferListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']

    def get_queryset(self):
        queryset = Offer.objects.select_related('user').prefetch_related('details')

        queryset = queryset.annotate(
            min_price=Min('details__price'),
            min_delivery_time=Min('details__delivery_time_in_days')
        )

        return queryset