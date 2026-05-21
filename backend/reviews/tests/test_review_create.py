from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from users.models import BusinessProfile, CustomerProfile
from reviews.models import Review


class ReviewCreateTests(APITestCase):
    """Test suite for POST /api/reviews/ endpoint"""
    
    def setUp(self):
        """Create test users"""
        self.business_user = User.objects.create_user(
            username='business1',
            password='pass123'
        )
        BusinessProfile.objects.create(user=self.business_user)
        self.business_token = Token.objects.create(user=self.business_user)
        
        self.customer_user = User.objects.create_user(
            username='customer1',
            password='pass456'
        )
        CustomerProfile.objects.create(user=self.customer_user)
        self.customer_token = Token.objects.create(user=self.customer_user)
        
        self.dual_user = User.objects.create_user(
            username='dual1',
            password='pass789'
        )
        CustomerProfile.objects.create(user=self.dual_user)
        BusinessProfile.objects.create(user=self.dual_user)
        self.dual_token = Token.objects.create(user=self.dual_user)
    
    def test_customer_can_create_review(self):
        """Customer should successfully create review"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        data = {
            'business_user': self.business_user.id,
            'rating': 5,
            'description': 'Excellent work!'
        }
        
        response = self.client.post('/api/reviews/', data, format='json')
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Review.objects.count(), 1)
        
        review = Review.objects.first()
        self.assertEqual(review.reviewer, self.customer_user)
        self.assertEqual(review.business_user, self.business_user)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.description, 'Excellent work!')
    
    def test_cannot_create_duplicate_review(self):
        """Should reject duplicate review for same business user"""
        Review.objects.create(
            reviewer=self.customer_user,
            business_user=self.business_user,
            rating=4,
            description='First review'
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        data = {
            'business_user': self.business_user.id,
            'rating': 5,
            'description': 'Second review attempt'
        }
        
        response = self.client.post('/api/reviews/', data, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Review.objects.count(), 1)
    
    def test_cannot_review_yourself(self):
        """User should not be able to review themselves"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.dual_token.key}')
        data = {
            'business_user': self.dual_user.id,
            'rating': 5,
            'description': 'Reviewing myself'
        }
        
        response = self.client.post('/api/reviews/', data, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('business_user', response.data)
        self.assertEqual(Review.objects.count(), 0)
    
    def test_business_user_cannot_create_review(self):
        """Business user without customer profile should be forbidden"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.business_token.key}')
        
        other_business = User.objects.create_user(username='business2', password='pass')
        BusinessProfile.objects.create(user=other_business)
        
        data = {
            'business_user': other_business.id,
            'rating': 5,
            'description': 'Great!'
        }
        
        response = self.client.post('/api/reviews/', data, format='json')
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Review.objects.count(), 0)
    
    def test_invalid_rating_rejected(self):
        """Rating outside 1-5 range should be rejected"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        data = {
            'business_user': self.business_user.id,
            'rating': 10,
            'description': 'Invalid rating'
        }
        
        response = self.client.post('/api/reviews/', data, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('rating', response.data)
    
    def test_missing_description_rejected(self):
        """Empty description should be rejected"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        data = {
            'business_user': self.business_user.id,
            'rating': 5,
            'description': ''
        }
        
        response = self.client.post('/api/reviews/', data, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('description', response.data)
    
    def test_non_existent_business_user_rejected(self):
        """Non-existent business_user should return 400"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        data = {
            'business_user': 9999,
            'rating': 5,
            'description': 'Review'
        }
        
        response = self.client.post('/api/reviews/', data, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('business_user', response.data)
    
    def test_unauthenticated_user_cannot_create_review(self):
        """User without token should get 401"""
        data = {
            'business_user': self.business_user.id,
            'rating': 5,
            'description': 'Review'
        }
        
        response = self.client.post('/api/reviews/', data, format='json')
        
        self.assertEqual(response.status_code, 401)