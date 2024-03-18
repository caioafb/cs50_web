from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Company(models.Model):
    name = models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_companies") # Creator of the company's account

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name
    
class CompanyUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="companies")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_users")
    access_level = models.IntegerField(default=1)

    def __str__(self):
         return f"{self.company} - {self.user}"