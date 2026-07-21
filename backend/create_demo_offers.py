"""
Create demo offers for testing
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from offers.models import Offer, OfferDetail
from users.models import BusinessProfile

# Get or create a business user
try:
    business_user = User.objects.filter(business_profile__isnull=False).first()
    if not business_user:
        business_user = User.objects.create_user(username='demo_business', password='demo123')
        BusinessProfile.objects.create(user=business_user)
        print(f"✓ Created business user: {business_user.username}")
    else:
        print(f"✓ Using existing business user: {business_user.username}")
except Exception as e:
    print(f"Error creating business user: {e}")
    exit(1)

# Demo offers data
demo_offers = [
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

# Create offers
created_count = 0
for offer_data in demo_offers:
    details_data = offer_data.pop('details')
    
    # Create offer
    offer = Offer.objects.create(
        user=business_user,
        title=offer_data['title'],
        description=offer_data['description']
    )
    
    # Create details
    for detail_data in details_data:
        OfferDetail.objects.create(offer=offer, **detail_data)
    
    created_count += 1
    print(f"✓ Created offer: {offer.title}")

print(f"\n✓ Created {created_count} demo offers with pricing tiers")
print(f"✓ All offers belong to user: {business_user.username}")
