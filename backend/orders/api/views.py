from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q

from orders.models import Order
from orders.api.serializers import OrderSerializer, OrderCreateSerializer, OrderUpdateSerializer
from orders.permissions import IsCustomerUser, IsOrderBusinessUser

class OrderListView(ListCreateAPIView):
    """API endpoint for listing and creating orders."""
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCustomerUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        return Order.objects.filter(
            Q(customer_user=user) | Q(business_user=user)
        ).select_related('customer_user', 'business_user', 'offer_detail')
    
class OrderDetailView(RetrieveUpdateDestroyAPIView):
    """API endpoint for retrieving, updating, and deleting specific order."""

    queryset = Order.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return OrderUpdateSerializer
        return OrderSerializer

    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [IsAuthenticated(), IsOrderBusinessUser()]
        elif self.request.method == 'DELETE':
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Order.objects.all()
        
        return Order.objects.filter(
            Q(customer_user=user) | Q(business_user=user)
        )