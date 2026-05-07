from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from users.models import BusinessProfile, CustomerProfile


class ProfileViewTests(APITestCase):
    def setUp(self):
        """Create test users with profiles"""
        # Create business user
        self.business_user = User.objects.create_user(
            username='bizuser',
            email='biz@test.com',
            password='pass123',
            first_name='John',
            last_name='Business'
        )
        self.business_profile = BusinessProfile.objects.create(
            user=self.business_user,
            location='Berlin',
            tel='123456789',
            description='I offer web development services',
            working_hours='9-17'
        )
        
        # Create customer user
        self.customer_user = User.objects.create_user(
            username='custuser',
            email='cust@test.com',
            password='pass456',
            first_name='Jane',
            last_name='Customer'
        )
        self.customer_profile = CustomerProfile.objects.create(
            user=self.customer_user,
            location='Munich',
            tel='987654321',
            description='Looking for web services',
            working_hours='10-18'
        )
        
        # Create token for authentication
        self.token = Token.objects.create(user=self.business_user)
    
    def test_authenticated_user_can_view_business_profile(self):
        """Test that an authenticated user can retrieve a business profile"""
        # Authenticate using token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        # Request the business user's profile
        response = self.client.get(f'/api/profile/{self.business_user.id}/')
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check all required fields are present
        self.assertEqual(response.data['user'], self.business_user.id)
        self.assertEqual(response.data['username'], 'bizuser')
        self.assertEqual(response.data['first_name'], 'John')
        self.assertEqual(response.data['last_name'], 'Business')
        self.assertEqual(response.data['email'], 'biz@test.com')
        self.assertEqual(response.data['location'], 'Berlin')
        self.assertEqual(response.data['tel'], '123456789')
        self.assertEqual(response.data['description'], 'I offer web development services')
        self.assertEqual(response.data['working_hours'], '9-17')
        self.assertEqual(response.data['type'], 'business')
        
        # Check that created_at is present
        self.assertIn('created_at', response.data)

    def test_authenticated_user_can_view_customer_profile(self):
        """Test that an authenticated user can retrieve a customer profile"""
        # Authenticate using token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        # Request the customer user's profile
        response = self.client.get(f'/api/profile/{self.customer_user.id}/')
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check all required fields are present
        self.assertEqual(response.data['user'], self.customer_user.id)
        self.assertEqual(response.data['username'], 'custuser')
        self.assertEqual(response.data['first_name'], 'Jane')
        self.assertEqual(response.data['last_name'], 'Customer')
        self.assertEqual(response.data['email'], 'cust@test.com')
        self.assertEqual(response.data['location'], 'Munich')
        self.assertEqual(response.data['tel'], '987654321')
        self.assertEqual(response.data['description'], 'Looking for web services')
        self.assertEqual(response.data['working_hours'], '10-18')
        self.assertEqual(response.data['type'], 'customer')
        
        # Check that created_at is present
        self.assertIn('created_at', response.data)

    def test_unauthenticated_user_cannot_view_profile(self):
        """Test that unauthenticated user gets 401"""
        response = self.client.get(f'/api/profile/{self.business_user.id}/')
        
        self.assertEqual(response.status_code, 401)
    
    def test_authenticated_user_gets_404_for_nonexistent_profile(self):
        """Test that requesting non-existent profile returns 404"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        response = self.client.get('/api/profile/9999/')
        
        self.assertEqual(response.status_code, 404)

    def test_empty_fields_return_empty_string_not_null(self):
        """Test that empty profile fields return '' instead of null"""
        # Create user without first_name/last_name
        empty_user = User.objects.create_user(username='emptyuser', password='pass')
        # Create profile with all optional fields empty (using defaults)
        BusinessProfile.objects.create(user=empty_user) 
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get(f'/api/profile/{empty_user.id}/')
        
        # Check that empty text fields return empty string, not null
        self.assertEqual(response.data['first_name'], '')
        self.assertEqual(response.data['last_name'], '')
        self.assertEqual(response.data['location'], '') 
        self.assertEqual(response.data['tel'], '')
        self.assertEqual(response.data['description'], '')
        self.assertEqual(response.data['working_hours'], '')
        
    