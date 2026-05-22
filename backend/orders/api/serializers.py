from rest_framework import serializers

from orders.models import Order
from offers.models import OfferDetail

class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model (read-only for list)"""

    class Meta:
        model = Order
        fields = [
            'id', 'customer_user', 'business_user',
            'title', 'revisions', 'delivery_time_in_days',
            'price', 'features', 'offer_type', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields

class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating orders from OfferDetail."""
    offer_detail_id = serializers.IntegerField()

    def validate_offer_detail_id(self, value):
        """Validate that the offer detail exists."""
        try:
            OfferDetail.objects.get(id=value)
        except OfferDetail.DoesNotExist:
            raise serializers.ValidationError("OfferDetail not found")
        return value
    
    def create(self, validated_data):
        """Create order from offer detail with auto-populated fields."""
        detail = OfferDetail.objects.get(id=validated_data['offer_detail_id'])

        customer_user = self.context['request'].user
        business_user = detail.offer.user

        order = Order.objects.create(
            customer_user=customer_user,
            business_user=business_user,
            offer_detail=detail,
            
            title=detail.title,
            revisions=detail.revisions,
            delivery_time_in_days=detail.delivery_time_in_days,
            price=detail.price,
            features=detail.features,
            offer_type=detail.offer_type,
            status='in_progress'
        )

        return order
    
    def to_representation(self, instance):
        """Return full order representation after creation."""
        return OrderSerializer(instance).data
    
class OrderUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating order status"""

    class Meta:
        model = Order
        fields = ['status']

    def to_representation(self, instance):
        """Return full order representation after update."""
        return OrderSerializer(instance).data