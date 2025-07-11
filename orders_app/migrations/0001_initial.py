# Generated by Django 5.2.3 on 2025-06-27 08:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('offers_app', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id',
                 models.BigAutoField(
                     auto_created=True,
                     primary_key=True,
                     serialize=False,
                     verbose_name='ID')),
                ('status',
                 models.CharField(
                     choices=[
                         ('pending',
                          'Pending'),
                         ('accepted',
                          'Accepted'),
                         ('completed',
                          'Completed'),
                         ('cancelled',
                          'Cancelled')],
                     default='pending',
                     max_length=20)),
                ('created_at',
                 models.DateTimeField(
                     auto_now_add=True)),
                ('updated_at',
                 models.DateTimeField(
                     auto_now=True)),
                ('customer',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='customer_orders',
                     to=settings.AUTH_USER_MODEL)),
                ('offer_detail',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE,
                     related_name='orders',
                     to='offers_app.offerdetail')),
            ],
            options={
                'db_table': 'orders_order',
                'ordering': ['-created_at'],
            },
        ),
    ]
