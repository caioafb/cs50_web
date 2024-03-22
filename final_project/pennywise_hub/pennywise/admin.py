from django.contrib import admin

from .models import User, Company, CompanyUser, Category, Account, Transaction

admin.site.register(User)
admin.site.register(Company)
admin.site.register(CompanyUser)
admin.site.register(Category)
admin.site.register(Account)
admin.site.register(Transaction)
