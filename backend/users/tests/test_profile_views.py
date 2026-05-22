from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
import io
from PIL import Image
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from users.models import BusinessProfile, CustomerProfile


class ProfileViewTests(APITestCase):
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
    
    def test_authenticated_user_can_view_business_profile(self):
        """Test that an authenticated user can retrieve a business profile"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get(f'/api/profile/{self.business_user.id}/')
        
        self.assertEqual(response.status_code, 200)
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
        self.assertIn('created_at', response.data)

    def test_authenticated_user_can_view_customer_profile(self):
        """Test that an authenticated user can retrieve a customer profile"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get(f'/api/profile/{self.customer_user.id}/')
        
        self.assertEqual(response.status_code, 200)
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
        empty_user = User.objects.create_user(username='emptyuser', password='pass')
        BusinessProfile.objects.create(user=empty_user)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get(f'/api/profile/{empty_user.id}/')
        
        self.assertEqual(response.data['first_name'], '')
        self.assertEqual(response.data['last_name'], '')
        self.assertEqual(response.data['location'], '')
        self.assertEqual(response.data['tel'], '')
        self.assertEqual(response.data['description'], '')
        self.assertEqual(response.data['working_hours'], '')
        
    def test_user_can_update_own_profile(self):
        """Test that a user can update their own profile"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        update_data = {
            'first_name': 'Johnny',
            'last_name': 'Updated',
            'location': 'Munich',
            'tel': '111222333',
            'description': 'Updated description',
            'working_hours': '10-20'
        }

        response = self.client.patch(
            f'/api/profile/{self.business_user.id}/',
            update_data,
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['first_name'], 'Johnny')
        self.assertEqual(response.data['last_name'], 'Updated')
        self.assertEqual(response.data['location'], 'Munich')
        self.assertEqual(response.data['tel'], '111222333')
        self.assertEqual(response.data['description'], 'Updated description')
        self.assertEqual(response.data['working_hours'], '10-20')

        self.business_user.refresh_from_db()
        self.assertEqual(self.business_user.first_name, 'Johnny')
        
        self.business_profile.refresh_from_db()
        self.assertEqual(self.business_profile.location, 'Munich')

    def test_user_can_not_update_different_profile(self):
        """Test that a user can't update their another profile"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        update_data = {
            'first_name': 'Johnny',
            'last_name': 'Updated',
            'location': 'Munich',
            'tel': '111222333',
            'description': 'Updated description',
            'working_hours': '10-20'
        }

        response = self.client.patch(
            f'/api/profile/{self.customer_user.id}/',  
            update_data,
            format='json'
        )

        self.assertEqual(response.status_code, 403)

    def test_unauthorized_user_can_not_update_profile(self):
        """Test that an unauthorized user can't update a profile"""

        update_data = {
            'first_name': 'Johnny',
            'last_name': 'Updated',
            'location': 'Munich',
            'tel': '111222333',
            'description': 'Updated description',
            'working_hours': '10-20'
        }

        response = self.client.patch(
            f'/api/profile/{self.business_user.id}/',
            update_data,
            format='json'
        )

        self.assertEqual(response.status_code, 401)

    def test_user_can_update_email(self):
        """Test that a user can update his email"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        update_data = {
            'email': 'test@test.de'
        }

        response = self.client.patch(
            f'/api/profile/{self.business_user.id}/',
            update_data,
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], 'test@test.de')
    
        self.business_user.refresh_from_db()
        self.assertEqual(self.business_user.email, 'test@test.de')

    def test_user_can_upload_profile_image(self):
        """Test that a user can upload a profile image file"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        image = Image.new('RGB', (100, 100), color='red')
        image_file = io.BytesIO()
        image.save(image_file, format='PNG')
        image_file.seek(0)
        
        uploaded_file = SimpleUploadedFile(
            'test_profile.png',
            image_file.read(),
            content_type='image/png'
        )
        
        update_data = {'file': uploaded_file}
        
        response = self.client.patch(
            f'/api/profile/{self.business_user.id}/',
            update_data,
            format='multipart'
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.business_profile.refresh_from_db()
        self.assertTrue(self.business_profile.file)
        self.assertIn('test_profile', self.business_profile.file.name) 

    def test_user_can_clear_fields_to_empty_string(self):
        """Test that updating fields to empty string works (not converted to null)"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        update_data = {
            'location': '',
            'tel': ''
        }
        
        response = self.client.patch(
            f'/api/profile/{self.business_user.id}/',
            update_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data['location'], '')
        self.assertEqual(response.data['tel'], '')
        
        self.business_profile.refresh_from_db()
        self.assertEqual(self.business_profile.location, '')
        self.assertEqual(self.business_profile.tel, '')