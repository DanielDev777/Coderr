from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from orders.models import Order
from orders.api.serializers import OrderSerializer

class OrderListView(ListAPIView):
    """API endpoint for listing orders."""

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        return Order.objects.filter(
            Q(customer_user=user) | Q(business_user=user)
        ).select_related('customer_user', 'business_user', 'offer_detail')