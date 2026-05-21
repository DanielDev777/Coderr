from django.urls import path
from .views import ReviewListView, ReviewDetailView, BaseInfoView

urlpatterns = [
    path('reviews/', ReviewListView.as_view(), name='review-list'),
    path('reviews/<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),
    path('base-info/', BaseInfoView.as_view(), name='base-info')
]