from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from reviews.models import Review
from users.models import BusinessProfile, CustomerProfile

class ReviewUpdateTests(APITestCase):
    """Test suite for PATCH /api/reviews/{id}/ endpoint"""
    
    def setUp(self):
        """Create test users and review"""
        self.business_user = User.objects.create_user(
            username='business1',
            password='pass123'
        )
        BusinessProfile.objects.create(user=self.business_user)
        
        self.customer_user1 = User.objects.create_user(
            username='customer1',
            password='pass456'
        )
        CustomerProfile.objects.create(user=self.customer_user1)
        self.customer1_token = Token.objects.create(user=self.customer_user1)
        
        self.customer_user2 = User.objects.create_user(
            username='customer2',
            password='pass789'
        )
        CustomerProfile.objects.create(user=self.customer_user2)
        self.customer2_token = Token.objects.create(user=self.customer_user2)
        
        self.review = Review.objects.create(
            reviewer=self.customer_user1,
            business_user=self.business_user,
            rating=4,
            description='Good service'
        )
    
    def test_reviewer_can_update_own_review(self):
        """Reviewer should be able to update their own review"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer1_token.key}')
        data = {
            'rating': 5,
            'description': 'Excellent service!'
        }
        
        response = self.client.patch(
            f'/api/reviews/{self.review.id}/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.description, 'Excellent service!')
    
    def test_partial_update_rating_only(self):
        """Should allow updating just rating"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer1_token.key}')
        data = {'rating': 5}
        
        response = self.client.patch(
            f'/api/reviews/{self.review.id}/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.description, 'Good service')
    
    def test_partial_update_description_only(self):
        """Should allow updating just description"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer1_token.key}')
        data = {'description': 'Updated description'}
        
        response = self.client.patch(
            f'/api/reviews/{self.review.id}/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 4)
        self.assertEqual(self.review.description, 'Updated description')
    
    def test_other_customer_cannot_update_review(self):
        """Different customer should not be able to update review"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer2_token.key}')
        data = {'rating': 1}
        
        response = self.client.patch(
            f'/api/reviews/{self.review.id}/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, 403)
        
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 4)
    
    def test_invalid_rating_rejected(self):
        """Rating outside 1-5 should be rejected"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer1_token.key}')
        data = {'rating': 10}
        
        response = self.client.patch(
            f'/api/reviews/{self.review.id}/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('rating', response.data)
    
    def test_unauthenticated_user_cannot_update(self):
        """User without token should get 401"""
        data = {'rating': 5}
        
        response = self.client.patch(
            f'/api/reviews/{self.review.id}/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, 401)