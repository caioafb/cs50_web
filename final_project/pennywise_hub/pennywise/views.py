from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError

from .models import User, Company, CompanyUser

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        company_name = request.POST["company"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "pennywise/register.html", {
                "message": "Passwords must match."
            })

        # Check if company name is taken
        if Company.objects.filter(name=company_name).exists():
            return render(request, "pennywise/register.html", {
                "message": "Company name already taken."
            })
        
        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "pennywise/register.html", {
                "message": "Username already taken."
            })
        
        # Create company
        company = Company(name=company_name, user=user)
        company.save()

        # Create company-user relation
        company_user = CompanyUser(user=user, company=company, access_level = 1)
        company_user.save()

        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "pennywise/register.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "pennywise/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "pennywise/login.html")
    

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def index(request):
    return render(request, "pennywise/index.html")