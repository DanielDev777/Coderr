from django.urls import path
from .views import OfferListView, OfferDetailView, OfferTierDetailView

urlpatterns = [
    path('offers/', OfferListView.as_view(), name='offer-list'),
    path('offers/<int:pk>/', OfferDetailView.as_view(), name='offer-detail'),
    path('offerdetails/<int:pk>/', OfferTierDetailView.as_view(), name='offer-tier-detail'),
]
