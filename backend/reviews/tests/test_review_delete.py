from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from users.models import BusinessProfile, CustomerProfile
from reviews.models import Review


class ReviewDeleteTests(APITestCase):
    """Test suite for DELETE /api/reviews/{id}/ endpoint"""
    
    def setUp(self):
        """Create test users and review"""
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        self.admin_token = Token.objects.create(user=self.admin_user)
        
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
    
    def test_admin_can_delete_review(self):
        """Admin user should be able to delete any review"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        review_id = self.review.id
        
        response = self.client.delete(f'/api/reviews/{review_id}/')
        
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Review.objects.count(), 0)
        self.assertFalse(Review.objects.filter(id=review_id).exists())
    
    def test_reviewer_cannot_delete_review(self):
        """Reviewer should not be able to delete their own review"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
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