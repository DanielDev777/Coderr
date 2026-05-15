from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from users.models import BusinessProfile, CustomerProfile
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io


class ProfileListsTests(APITestCase):
    def setUp(self):
        """Create test users with profiles"""
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

        self.token = Token.objects.create(user=self.business_user)

    def test_authenticated_user_can_access_business_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        response = self.client.get(f'/api/profiles/business/')

        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_user_can_not_access_business_profile(self):
        response = self.client.get(f'/api/profiles/business/')

        self.assertEqual(response.status_code, 401)

    def test_only_business_profiles_returned_not_customers(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        biz_user = User.objects.create_user(username='biz')
        BusinessProfile.objects.create(user=biz_user)

        cust_user = User.objects.create_user(username='cust')
        CustomerProfile.objects.create(user=cust_user)

        response = self.client.get('/api/profiles/business/')

        results = response.data['results']
        self.assertEqual(len(results), 2)
        
        usernames = [profile['username'] for profile in results]
        self.assertIn('biz', usernames)
        self.assertIn('bizuser', usernames)
        
        for profile in results:
            self.assertEqual(profile['type'], 'business')

    def test_empty_fields_return_empty_string_not_null(self):
        """Test that empty profile fields return '' instead of null"""
        empty_user = User.objects.create_user(username='emptyuser', password='pass')
        BusinessProfile.objects.create(user=empty_user)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get(f'/api/profiles/business/')

        empty_profile = None
        for profile in response.data['results']:
            if profile['username'] == 'emptyuser':
                empty_profile = profile
                break
        
        self.assertIsNotNone(empty_profile)
        
        self.assertEqual(empty_profile['first_name'], '')
        self.assertEqual(empty_profile['last_name'], '')
        self.assertEqual(empty_profile['location'], '')
        self.assertEqual(empty_profile['tel'], '')
        self.assertEqual(empty_profile['description'], '')
        self.assertEqual(empty_profile['working_hours'], '')

    def test_list_returns_multiple_business_users(self):
        """Test that all business users are returned in the list"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        for i in range(3):
            user = User.objects.create_user(
                username=f'business{i}',
                first_name=f'Business{i}',
                last_name=f'User{i}'
            )
            BusinessProfile.objects.create(
                user=user,
                location=f'City{i}',
                description=f'Description {i}'
            )
        
        response = self.client.get('/api/profiles/business/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 4)
        
        results = response.data['results']
        usernames = [profile['username'] for profile in results]
        self.assertIn('bizuser', usernames)
        self.assertIn('business0', usernames)
        self.assertIn('business1', usernames)
        self.assertIn('business2', usernames)