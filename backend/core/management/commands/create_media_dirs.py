import os
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Creates media directories if they do not exist'

    def handle(self, *args, **options):
        """Create all required media directories"""
        media_dirs = [
            settings.MEDIA_ROOT,
            os.path.join(settings.MEDIA_ROOT, 'offer_images'),
            os.path.join(settings.MEDIA_ROOT, 'profile_pictures'),
        ]

        for directory in media_dirs:
            if not os.path.exists(directory):
                os.makedirs(directory, mode=0o755)
                self.stdout.write(
                    self.style.SUCCESS(f'Created directory: {directory}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Directory already exists: {directory}')
                )

        self.stdout.write(
            self.style.SUCCESS('Media directories setup complete!')
        )
