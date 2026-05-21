from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from users.models import BusinessProfile, CustomerProfile
from reviews.models import Review


class ReviewListTests(APITestCase):
    """Test suite for GET /api/reviews/ endpoint"""
    
    def setUp(self):
        """Create test users and reviews"""
        self.business_user1 = User.objects.create_user(
            username='business1',
            password='pass123'
        )
        BusinessProfile.objects.create(user=self.business_user1)
        
        self.business_user2 = User.objects.create_user(
            username='business2',
            password='pass456'
        )
        BusinessProfile.objects.create(user=self.business_user2)
        
        self.customer_user1 = User.objects.create_user(
            username='customer1',
            password='pass789'
        )
        CustomerProfile.objects.create(user=self.customer_user1)
        self.customer1_token = Token.objects.create(user=self.customer_user1)
        
        self.customer_user2 = User.objects.create_user(
            username='customer2',
            password='pass101'
        )
        CustomerProfile.objects.create(user=self.customer_user2)
        
        self.review1 = Review.objects.create(
            reviewer=self.customer_user1,
            business_user=self.business_user1,
            rating=5,
            description='Excellent service!'
        )
        self.review2 = Review.objects.create(
            reviewer=self.customer_user2,
            business_user=self.business_user1,
            rating=3,
            description='Good but could be better'
        )
        self.review3 = Review.objects.create(
            reviewer=self.customer_user1,
            business_user=self.business_user2,
            rating=4,
            description='Very professional'
        )
    
    def test_list_all_reviews(self):
        """Should return all reviews when no filters applied"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer1_token.key}')
        
        response = self.client.get('/api/reviews/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 3)
    
    def test_filter_by_business_user(self):
        """Should return only reviews for specific business user"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer1_token.key}')
        
        response = self.client.get(f'/api/reviews/?business_user_id={self.business_user1.id}')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)
        
        review_ids = [review['id'] for review in response.data['results']]
        self.assertIn(self.review1.id, review_ids)
        self.assertIn(self.review2.id, review_ids)
        self.assertNotIn(self.review3.id, review_ids)
    
    def test_filter_by_reviewer(self):
        """Should return only reviews by specific customer"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer1_token.key}')
        
        response = self.client.get(f'/api/reviews/?reviewer_id={self.customer_user1.id}')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)
        
        review_ids = [review['id'] for review in response.data['results']]
        self.assertIn(self.review1.id, review_ids)
        self.assertNotIn(self.review2.id, review_ids)
        self.assertIn(self.review3.id, review_ids)
    
    def test_sort_by_rating_descending(self):
        """Should return reviews sorted by highest rating first"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer1_token.key}')
        
        response = self.client.get('/api/reviews/?ordering=-rating')
        
        self.assertEqual(response.status_code, 200)
        ratings = [review['rating'] for review in response.data['results']]
        self.assertEqual(ratings, [5, 4, 3])
    
    def test_sort_by_rating_ascending(self):
        """Should return reviews sorted by lowest rating first"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer1_token.key}')
        
        response = self.client.get('/api/reviews/?ordering=rating')
        
        self.assertEqual(response.status_code, 200)
        ratings = [review['rating'] for review in response.data['results']]
        self.assertEqual(ratings, [3, 4, 5])
    
    def test_unauthenticated_user_cannot_list_reviews(self):
        """User without token should get 401"""
        response = self.client.get('/api/reviews/')
        
        self.assertEqual(response.status_code, 401)