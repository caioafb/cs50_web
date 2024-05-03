# Generated by Django 5.0 on 2024-04-23 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pennywise', '0015_alter_transaction_replicate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='replicate',
            field=models.CharField(choices=[('O', 'Once'), ('M', 'Monthly'), ('B', 'Bimonthly'), ('Q', 'Quarterly'), ('Y', 'Yearly')], default='O', max_length=1),
        ),
    ]
