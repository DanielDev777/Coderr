import django_filters
from .models import Offer
from django.db.models import Min

class OfferFilter(django_filters.FilterSet):
    creator_id = django_filters.NumberFilter(field_name='user', lookup_expr='exact')
    max_delivery_time = django_filters.NumberFilter(method='filter_by_max_delivery')
    
    def filter_by_max_delivery(self, queryset, name, value):
        queryset = queryset.annotate(
            min_delivery=Min('details__delivery_time_in_days')
        )

        return queryset.filter(min_delivery__lte=value)
    
    class Meta:
        model = Offer
        fields = ['creator_id', 'max_delivery_time']
