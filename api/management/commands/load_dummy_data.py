from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import Profile

class Command(BaseCommand):
    help = 'Load dummy data into the database'

    def handle(self, *args, **options):
        # Superuser anlegen
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
        # Beispielkunde
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
        self.stdout.write(self.style.SUCCESS('Dummy data loaded.'))
