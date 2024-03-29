# Generated by Django 5.0 on 2024-03-19 21:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pennywise', '0002_company_companyuser'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='company',
            options={'verbose_name_plural': 'Companies'},
        ),
        migrations.AlterField(
            model_name='company',
            name='name',
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to='pennywise.company')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('type', models.CharField(choices=[('P', 'Payable'), ('R', 'Receivable')], max_length=1)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='pennywise.company')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('due_date', models.DateField()),
                ('description', models.CharField(max_length=255)),
                ('payment_info', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=8)),
                ('installments', models.IntegerField(null=True)),
                ('current_installment', models.IntegerField(null=True)),
                ('repeat', models.CharField(choices=[('O', 'Once'), ('M', 'Monthly'), ('Q', 'Quarterly'), ('Y', 'Yearly')], default='O', max_length=1)),
                ('has_repeated', models.BooleanField(default=False)),
                ('parent_id', models.IntegerField(null=True)),
                ('settle_date', models.DateField()),
                ('settle_description', models.CharField(max_length=255)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='category_transactions', to='pennywise.category')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company_transactions', to='pennywise.company')),
                ('settle_account', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='account_transactions', to='pennywise.account')),
                ('settle_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='settle_user_transactions', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_transactions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='account',
            constraint=models.UniqueConstraint(fields=('name', 'company'), name='company_account'),
        ),
        migrations.AddConstraint(
            model_name='category',
            constraint=models.UniqueConstraint(fields=('name', 'company'), name='company_category'),
        ),
    ]
