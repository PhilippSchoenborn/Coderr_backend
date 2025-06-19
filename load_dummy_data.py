from django.contrib.auth.models import User
from api.models import Profile, Offer
from django.core.files.base import ContentFile
import base64
import os

def run():
    # Create superuser
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')
        Profile.objects.create(
            user=admin,
            username='admin',
            first_name='Admin',
            last_name='User',
            file='',
            location='Berlin',
            tel='123456789',
            description='Admin profile',
            working_hours='9-17',
            type='business',
            email='admin@example.com',
        )
    # Create example customer
    if not User.objects.filter(username='customer1').exists():
        customer = User.objects.create_user('customer1', 'customer1@example.com', 'customerpass')
        Profile.objects.create(
            user=customer,
            username='customer1',
            first_name='Jane',
            last_name='Doe',
            file='',
            location='Hamburg',
            tel='987654321',
            description='Customer profile',
            working_hours='10-18',
            type='customer',
            email='customer1@example.com',
        )
    # Helper to add an image from a local file (put images in a 'media/dummy/' folder)
    def get_image_file(filename):
        path = os.path.join('media', 'dummy', filename)
        if os.path.exists(path):
            with open(path, 'rb') as f:
                return ContentFile(f.read(), name=filename)
        return None
    # Create detailed offers (basic, standard, premium) with images
    offers = [
        {
            'title': 'Logo Design - Basic',
            'description': 'Simple logo design with 1 concept and 1 revision.',
            'price': 49.99,
            'image': get_image_file('logo_basic.jpg'),
        },
        {
            'title': 'Logo Design - Standard',
            'description': 'Logo design with 3 concepts and 3 revisions, color variations included.',
            'price': 129.99,
            'image': get_image_file('logo_standard.jpg'),
        },
        {
            'title': 'Logo Design - Premium',
            'description': 'Premium logo design with unlimited revisions, brand guide, and all formats.',
            'price': 299.99,
            'image': get_image_file('logo_premium.jpg'),
        },
        {
            'title': 'Website Development - Basic',
            'description': 'One-page website, responsive design, 1 revision.',
            'price': 299.00,
            'image': get_image_file('web_basic.jpg'),
        },
        {
            'title': 'Website Development - Standard',
            'description': 'Up to 5 pages, contact form, 3 revisions, SEO basics.',
            'price': 899.00,
            'image': get_image_file('web_standard.jpg'),
        },
        {
            'title': 'Website Development - Premium',
            'description': 'Full website, unlimited pages, CMS, premium SEO, unlimited revisions.',
            'price': 1999.00,
            'image': get_image_file('web_premium.jpg'),
        },
        {
            'title': 'Social Media Marketing - Basic',
            'description': 'Content plan for 1 platform, 5 posts, 1 revision.',
            'price': 99.00,
            'image': get_image_file('smm_basic.jpg'),
        },
        {
            'title': 'Social Media Marketing - Standard',
            'description': 'Content for 2 platforms, 12 posts, 3 revisions, analytics report.',
            'price': 249.00,
            'image': get_image_file('smm_standard.jpg'),
        },
        {
            'title': 'Social Media Marketing - Premium',
            'description': 'Full strategy, all platforms, unlimited posts, ads management, unlimited revisions.',
            'price': 599.00,
            'image': get_image_file('smm_premium.jpg'),
        },
    ]
    admin = User.objects.get(username='admin')
    for offer in offers:
        if not Offer.objects.filter(title=offer['title']).exists():
            Offer.objects.create(
                title=offer['title'],
                description=offer['description'],
                price=offer['price'],
                image=offer['image'],
                owner=admin,
            )
    print('Dummy data with detailed offers and images loaded.')
