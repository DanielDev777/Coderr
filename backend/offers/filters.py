import django_filters
from .models import Offer
from django.db.models import Min

class OfferFilter(django_filters.FilterSet):
    """Custom filter for offers by creator, minimum price, and maximum delivery time."""
    creator_id = django_filters.NumberFilter(field_name='user', lookup_expr='exact')
    min_price = django_filters.NumberFilter(method='filter_by_min_price')
    max_delivery_time = django_filters.NumberFilter(method='filter_by_max_delivery')
    
    def filter_by_min_price(self, queryset, name, value):
        """Filter offers by minimum price across all tiers.""
        queryset = queryset.annotate(
            minimum_price=Min('details__price')
        )
        return queryset.filter(minimum_price__gte=value)
    
    def filter_by_max_delivery(self, queryset, name, value):
        """Filter offers by maximum delivery time across all tiers."""
        queryset = queryset.annotate(
            min_delivery=Min('details__delivery_time_in_days')
        )

        return queryset.filter(min_delivery__lte=value)
    
    class Meta:
        model = Offer
        fields = ['creator_id', 'min_price', 'max_delivery_time']
