from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from auctions.models import *

from .models import User

class DateInput(forms.DateInput):
    input_type = "date"

class NewListingForm(forms.Form):
    title = forms.CharField(label="Title", max_length=255)
    starting_bid = forms.DecimalField(label="Price", max_digits=7, decimal_places=2)
    due_date = forms.DateField(label="Due Date", widget=DateInput)
    image = forms.CharField(label="Image URL", max_length=255, widget=forms.TextInput({"placeholder": "(Optional)"}), required=False)
    description = forms.CharField(label="Description", widget=forms.Textarea)
    category = forms.ModelChoiceField(label="Category", widget=forms.Select, queryset=Category.objects.all().order_by("name"))

class NewCategoryForm(forms.Form):
    name = forms.CharField(label="Name", max_length=30)
    image = forms.CharField(label="Image URL", max_length=255)


def index(request):

    return render(request, "auctions/index.html")


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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    

@login_required
def create_listing(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            user = request.user
            title = form.cleaned_data["title"]
            starting_bid = form.cleaned_data["starting_bid"]
            due_date = form.cleaned_data["due_date"]
            image = form.cleaned_data["image"]
            description = form.cleaned_data["description"]
            category = form.cleaned_data["category"]
            listing = Listing(user=user, title=title, starting_bid=starting_bid, due_date=due_date, image_url=image, description=description, category=category)
            listing.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/create_listing.html", {
                "form": form
            })
        
    has_categories = Category.objects.all()
    return render(request, "auctions/create_listing.html", {
        "form": NewListingForm(),
        "has_categories": has_categories
    })


@login_required
def new_category(request):
    if request.method == "POST":
        form = NewCategoryForm(request.POST)
        if form.is_valid():
            new_name = form.cleaned_data["name"]
            new_image = form.cleaned_data["image"]
            category = Category(name=new_name, image_url=new_image)
            category.save()
            return HttpResponseRedirect(reverse("create_listing"))
        
    return render(request, "auctions/new_category.html", {
        "form": NewCategoryForm()
    })