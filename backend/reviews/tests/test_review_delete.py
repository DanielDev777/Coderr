from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from reviews.models import Review
from users.models import BusinessProfile, CustomerProfile


class ReviewDeleteTests(APITestCase):
    """Test suite for DELETE /api/reviews/{id}/ endpoint"""
    
    def setUp(self):
        """Create test users and review"""
        self.business_user = User.objects.create_user(
            username='business1',
            password='pass123'
        )
        BusinessProfile.objects.create(user=self.business_user)
        
        self.customer_user = User.objects.create_user(
            username='customer1',
            password='pass456'
        )
        CustomerProfile.objects.create(user=self.customer_user)
        self.customer_token = Token.objects.create(user=self.customer_user)
        
        self.review = Review.objects.create(
            reviewer=self.customer_user,
            business_user=self.business_user,
            rating=5,
            description='Great work!'
        )
    
    def test_reviewer_can_delete_own_review(self):
        """Reviewer should be able to delete their own review"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        review_id = self.review.id
        
        response = self.client.delete(f'/api/reviews/{review_id}/')
        
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Review.objects.count(), 0)
        self.assertFalse(Review.objects.filter(id=review_id).exists())
    
    def test_other_customer_cannot_delete_review(self):
        """Different customer should not be able to delete review"""
        other_customer = User.objects.create_user(
            username='customer2',
            password='pass789'
        )
        CustomerProfile.objects.create(user=other_customer)
        other_token = Token.objects.create(user=other_customer)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {other_token.key}')
        review_id = self.review.id
        
        response = self.client.delete(f'/api/reviews/{review_id}/')
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Review.objects.count(), 1)
        self.assertTrue(Review.objects.filter(id=review_id).exists())
    
    def test_business_user_cannot_delete_review(self):
        """Business user should not be able to delete reviews"""
        business_token = Token.objects.create(user=self.business_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {business_token.key}')
        review_id = self.review.id
        
        response = self.client.delete(f'/api/reviews/{review_id}/')
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Review.objects.count(), 1)
    
    def test_unauthenticated_user_cannot_delete(self):
        """User without token should get 401"""
        review_id = self.review.id
        
        response = self.client.delete(f'/api/reviews/{review_id}/')
        
        self.assertEqual(response.status_code, 401)