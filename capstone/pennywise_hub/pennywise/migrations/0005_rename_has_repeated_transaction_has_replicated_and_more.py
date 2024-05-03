# Generated by Django 5.0 on 2024-03-20 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pennywise', '0004_transaction_settle_receipt'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='has_repeated',
            new_name='has_replicated',
        ),
        migrations.RenameField(
            model_name='transaction',
            old_name='repeat',
            new_name='replicate',
        ),
        migrations.AlterField(
            model_name='category',
            name='type',
            field=models.CharField(choices=[('E', 'Expense'), ('I', 'Income')], max_length=1),
        ),
    ]
