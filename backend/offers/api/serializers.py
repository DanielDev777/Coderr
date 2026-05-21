from rest_framework import serializers
from offers.models import Offer, OfferDetail


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


class OfferDetailSerializer(serializers.ModelSerializer):
    """Serializer for individual OfferDetail instances"""
    class Meta:
        model = OfferDetail
        fields = [
            'id',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type'
        ]
        read_only_fields = ['id']


class OfferCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating offers with nested details."""
    details = OfferDetailSerializer(many=True, write_only=False)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']
        read_only_fields = ['id']

    def validate_details(self, value):
        if len(value) != 3:
            raise serializers.ValidationError(
                "An offer must have exactly 3 details (basic, standard, premium)"
            )

        offer_types = [detail['offer_type'] for detail in value]

        if len(offer_types) != len(set(offer_types)):
            raise serializers.ValidationError(
                "Each detail must have a unique offer_type. Found duplicates."
            )

        required_types = {'basic', 'standard', 'premium'}
        provided_types = set(offer_types)

        if provided_types != required_types:
            missing = required_types - provided_types
            raise serializers.ValidationError(
                f"Missing offer_types: {missing}. Must include basic, standard, and premium."
            )

        return value

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)

        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)

        return offer


class OfferUpdateSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True, required=False)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if details_data is not None:
            for detail_data in details_data:
                offer_type = detail_data.get('offer_type')

                if offer_type:
                    try:
                        detail = OfferDetail.objects.get(
                            offer_type=offer_type,
                            offer=instance
                        )
                        for attr, value in detail_data.items():
                            setattr(detail, attr, value)
                        detail.save()
                    except OfferDetail.DoesNotExist:
                        pass

        return instance
