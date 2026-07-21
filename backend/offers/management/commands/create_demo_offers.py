from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from offers.models import Offer, OfferDetail

GUEST_BUSINESS_USERNAME = 'business'

DEMO_OFFERS = [
    {
        'title': 'Professional Website Development',
        'description': 'Full-stack web development with modern technologies',
        'details': [
            {'title': 'Basic', 'revisions': 2, 'delivery_time_in_days': 7, 'price': '500.00', 'offer_type': 'basic'},
            {'title': 'Standard', 'revisions': 4, 'delivery_time_in_days': 14, 'price': '1000.00', 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 8, 'delivery_time_in_days': 21, 'price': '2000.00', 'offer_type': 'premium'},
        ]
    },
    {
        'title': 'Logo Design',
        'description': 'Creative logo design for your brand',
        'details': [
            {'title': 'Basic', 'revisions': 3, 'delivery_time_in_days': 3, 'price': '50.00', 'offer_type': 'basic'},
            {'title': 'Standard', 'revisions': 5, 'delivery_time_in_days': 5, 'price': '100.00', 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 10, 'delivery_time_in_days': 7, 'price': '200.00', 'offer_type': 'premium'},
        ]
    },
    {
        'title': 'SEO Optimization',
        'description': 'Improve your website search engine ranking',
        'details': [
            {'title': 'Basic', 'revisions': 1, 'delivery_time_in_days': 14, 'price': '300.00', 'offer_type': 'basic'},
            {'title': 'Standard', 'revisions': 2, 'delivery_time_in_days': 21, 'price': '600.00', 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 4, 'delivery_time_in_days': 30, 'price': '1200.00', 'offer_type': 'premium'},
        ]
    },
    {
        'title': 'Mobile App Development',
        'description': 'Native iOS and Android app development',
        'details': [
            {'title': 'Basic', 'revisions': 3, 'delivery_time_in_days': 30, 'price': '3000.00', 'offer_type': 'basic'},
            {'title': 'Standard', 'revisions': 5, 'delivery_time_in_days': 45, 'price': '5000.00', 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 10, 'delivery_time_in_days': 60, 'price': '8000.00', 'offer_type': 'premium'},
        ]
    },
    {
        'title': 'Content Writing',
        'description': 'Professional content writing for blogs and websites',
        'details': [
            {'title': 'Basic', 'revisions': 2, 'delivery_time_in_days': 2, 'price': '30.00', 'offer_type': 'basic'},
            {'title': 'Standard', 'revisions': 3, 'delivery_time_in_days': 3, 'price': '60.00', 'offer_type': 'standard'},
            {'title': 'Premium', 'revisions': 5, 'delivery_time_in_days': 5, 'price': '100.00', 'offer_type': 'premium'},
        ]
    },
]


class Command(BaseCommand):
    help = 'Creates demo offers for the guest business user used by the frontend guest login'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            default=GUEST_BUSINESS_USERNAME,
            help=f'Business user the offers belong to (default: {GUEST_BUSINESS_USERNAME})'
        )

    def handle(self, *args, **options):
        """Create demo offers, skipping offers the user already has"""
        username = options['username']

        try:
            business_user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(
                f'User "{username}" does not exist. Run "manage.py create_guest_users" first.'
            )

        if not hasattr(business_user, 'business_profile'):
            raise CommandError(f'User "{username}" has no business profile.')

        created_count = 0
        for offer_data in DEMO_OFFERS:
            offer, created = Offer.objects.get_or_create(
                user=business_user,
                title=offer_data['title'],
                defaults={'description': offer_data['description']}
            )

            if not created:
                self.stdout.write(
                    self.style.WARNING(f'Offer already exists, skipping: {offer.title}')
                )
                continue

            for detail_data in offer_data['details']:
                OfferDetail.objects.create(offer=offer, **detail_data)

            created_count += 1
            self.stdout.write(self.style.SUCCESS(f'Created offer: {offer.title}'))

        self.stdout.write(
            self.style.SUCCESS(
                f'Created {created_count} demo offers for user: {business_user.username}'
            )
        )
