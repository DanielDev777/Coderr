from rest_framework import serializers

class OfferDetailListSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    url = serializers.SerializerMethodField()
    
    def get_url(self, obj):
        return f'/api/offerdetails/{obj.id}/'
    
    
class OfferListSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    user = serializers.IntegerField(source='user.id', read_only=True)
    title = serializers.CharField()
    image = serializers.ImageField(required=False)
    description = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()
    details = OfferDetailListSerializer(many=True, read_only=True)

    def get_min_price(self, obj):
        return obj.min_price
    
    def get_min_delivery_time(self, obj):
        return obj.min_delivery_time
    
    def get_user_details(self, obj):
        return {
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'username': obj.user.username
        }