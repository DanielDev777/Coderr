from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from offers.models import Offer
from reviews.models import Review
from users.models import BusinessProfile, CustomerProfile


class BaseInfoTests(APITestCase):
    """Test suite for GET /api/base-info/ endpoint"""
    
    def setUp(self):
        """Create test data for platform statistics"""
        for i in range(3):
            business_user = User.objects.create_user(
                username=f'business{i+1}',
                password='pass123'
            )
            BusinessProfile.objects.create(user=business_user)
            
            for j in range(2):
                Offer.objects.create(
                    user=business_user,
                    title=f'Offer {i+1}-{j+1}',
                    description='Test offer'
                )
        
        customer1 = User.objects.create_user(username='customer1', password='pass')
        CustomerProfile.objects.create(user=customer1)
        customer2 = User.objects.create_user(username='customer2', password='pass')
        CustomerProfile.objects.create(user=customer2)
        
        business_for_reviews = User.objects.get(username='business1')
        Review.objects.create(
            reviewer=customer1,
            business_user=business_for_reviews,
            rating=5,
            description='Excellent!'
        )
        Review.objects.create(
            reviewer=customer2,
            business_user=business_for_reviews,
            rating=4,
            description='Good'
        )
    
    def test_returns_correct_platform_statistics(self):
        """Should return platform-wide statistics"""
        response = self.client.get('/api/base-info/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['review_count'], 2)
        self.assertAlmostEqual(float(response.data['average_rating']), 4.5, places=1)
        self.assertEqual(response.data['business_profile_count'], 3)
        self.assertEqual(response.data['offer_count'], 6)
    
    def test_works_without_authentication(self):
        """Should work without authentication (public endpoint)"""
        response = self.client.get('/api/base-info/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('review_count', response.data)
        self.assertIn('average_rating', response.data)
        self.assertIn('business_profile_count', response.data)
        self.assertIn('offer_count', response.data)