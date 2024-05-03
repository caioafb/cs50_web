from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime
from dateutil.relativedelta import relativedelta

class User(AbstractUser):
    pass

class Company(models.Model):
    name = models.CharField(max_length=30)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_companies") # Creator of the company's account

    class Meta:
        verbose_name_plural = "Companies"
        constraints = [
            models.UniqueConstraint(fields=["name", "user"], name="user_company")
        ]

    def __str__(self):
        return self.name
    
class CompanyUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="companies")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_users")
    access_level = models.IntegerField(default=1)

    def __str__(self):
         return f"{self.company} - {self.user}"
    
class Category(models.Model):
    TYPE_CHOICES = {
        "E": "Expense",
        "I": "Income"
    }

    name = models.CharField(max_length=30)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="categories")

    class Meta:
        verbose_name_plural = "Categories"
        constraints = [
            models.UniqueConstraint(fields=["name", "company"], name="company_category")
        ]
    
    def __str__(self):
        return f"{self.company} - {self.type} - {self.name}"

class Account(models.Model):
    name = models.CharField(max_length=30)
    balance = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="accounts")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name", "company"], name="company_account")
        ]

    def __str__(self):
        return f"{self.company} - {self.name}"
    
    
class MonthlyAccountBalance(models.Model):
    balance = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    month_year = models.DateField() # Saving the first day of the month, example: April 2024 will be saved as 2024-04-01)
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="monthly_balances")

    def __str__(self):
        return f"{self.account} - {self.month_year.month}/{self.month_year.year} - {self.balance}"


class Transaction(models.Model):
    REPLICATE_CHOICES = {
        "O": "Once",
        "M": "Monthly",
        "B": "Bimonthly",
        "Q": "Quarterly",
        "Y": "Yearly"
    }

    due_date = models.DateField()
    description = models.CharField(max_length=255)
    payment_info = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    installments = models.IntegerField(null=True, blank=True)
    current_installment = models.IntegerField(null=True, blank=True)
    replicate = models.CharField(max_length=1, choices=REPLICATE_CHOICES, default="O") # Expenses with more than one installment can only have this set to "once" or "yearly" (if more than 12 installments, only to "once")
    has_replicated = models.BooleanField(default=False)
    parent_id = models.IntegerField(null=True, blank=True) # If replicated, stores parent's transaction id for replicating purposes
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="category_transactions")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_transactions")
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="user_transactions")
    settle_account = models.ForeignKey(Account, null=True, blank=True, on_delete=models.PROTECT, related_name="account_transactions")
    settle_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="settle_user_transactions")
    settle_date = models.DateField(null=True, blank=True)
    settle_description = models.CharField(null=True, blank=True, max_length=255)
    settle_receipt = models.ImageField(null=True, blank=True, upload_to="pennywise/files/receipts")
    payment_slip = models.ImageField(null=True, blank=True, upload_to="pennywise/files/payment_slips")
    
    def has_expired(self):
        today = datetime.strptime("2024-04-30", "%Y-%m-%d").date()
        #today = datetime.today().date()
        return self.due_date < today
    
    def is_last_day_of_month(self):
        date = self.due_date.replace(day=1) + relativedelta(months=1) - relativedelta(days=1)
        return date == self.due_date
    
    def is_weekend(self):
        return self.due_date.weekday() > 4
    
    def __str__(self):
        return f"{self.company} - {self.id}"
    
class Timer(models.Model):
    db_date = models.DateField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="timer")

    def __str__(self):
        return f"{self.db_date}"