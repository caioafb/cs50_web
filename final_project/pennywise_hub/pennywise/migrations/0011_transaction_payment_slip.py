# Generated by Django 5.0 on 2024-04-08 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pennywise', '0010_monthlyaccountbalance'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='payment_slip',
            field=models.ImageField(blank=True, null=True, upload_to='pennywise/files/payment_slips'),
        ),
    ]