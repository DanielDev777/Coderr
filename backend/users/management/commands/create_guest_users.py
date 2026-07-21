from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from users.models import BusinessProfile, CustomerProfile

GUEST_USERS = [
    {
        'username': 'customer',
        'password': 'asdasd12345',
        'email': 'customer@coderr.local',
        'first_name': 'Guest',
        'last_name': 'Customer',
        'profile_model': CustomerProfile,
    },
    {
        'username': 'business',
        'password': 'asdasd24',
        'email': 'business@coderr.local',
        'first_name': 'Guest',
        'last_name': 'Business',
        'profile_model': BusinessProfile,
    },
]


class Command(BaseCommand):
    help = 'Creates the guest demo users used by the frontend guest login'

    def handle(self, *args, **options):
        """Create guest users and their profiles, resetting the password if they exist"""
        for guest in GUEST_USERS:
            profile_model = guest['profile_model']

            user, created = User.objects.get_or_create(
                username=guest['username'],
                defaults={
                    'email': guest['email'],
                    'first_name': guest['first_name'],
                    'last_name': guest['last_name'],
                }
            )

            user.set_password(guest['password'])
            user.is_active = True
            user.save()

            profile_model.objects.get_or_create(user=user)

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created guest user: {user.username}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Updated password for existing user: {user.username}')
                )

        self.stdout.write(
            self.style.SUCCESS('Guest users setup complete!')
        )
