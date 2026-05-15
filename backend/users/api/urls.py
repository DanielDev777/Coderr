from django.urls import path
from .views import RegistrationView, LoginView, ProfileDetailView, BusinessProfileView

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name='profile'),
    path('profiles/business/', BusinessProfileView.as_view(), name="business_profiles")
]
