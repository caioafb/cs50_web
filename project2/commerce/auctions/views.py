from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
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

class NewBidForm(forms.Form):
    value = forms.DecimalField(label="", widget=forms.NumberInput(attrs={"placeholder": "Bid"}), max_digits=7, decimal_places=2)
    option = forms.CharField(widget=forms.HiddenInput(), initial="bid")

class NewCommentForm(forms.Form):
    text = forms.CharField(label="", widget=forms.Textarea(attrs={"placeholder": " comment here", "rows":1, "cols":75}))
    option = forms.CharField(widget=forms.HiddenInput(), initial="comment")

def is_an_url(url_string: str) -> bool:
    validate_url = URLValidator()
    try:
        validate_url(url_string)
    except ValidationError:
        return False
    return True


def index(request):
    active_listings = Listing.objects.all().filter(is_active=True)
    inactive_listings = Listing.objects.all().filter(is_active=False)
    return render(request, "auctions/index.html", {
        "active_listings": active_listings,
        "inactive_listings": inactive_listings
    })


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
            # Save new listing on database
            title = form.cleaned_data["title"]
            starting_bid = form.cleaned_data["starting_bid"]
            due_date = form.cleaned_data["due_date"]
            image = form.cleaned_data["image"]
            if not is_an_url(image):
                image = "https://icon-library.com/images/no-picture-available-icon/no-picture-available-icon-1.jpg"
            description = form.cleaned_data["description"]
            category = form.cleaned_data["category"]
            listing = Listing(user=request.user, title=title, starting_bid=starting_bid, due_date=due_date, image_url=image, description=description, category=category)
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
        # Save new category on database
        form = NewCategoryForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            image = form.cleaned_data["image"]
            if not is_an_url(image):
                image = "https://icon-library.com/images/no-picture-available-icon/no-picture-available-icon-1.jpg"
            category = Category(name=name, image_url=image)
            category.save()
            return HttpResponseRedirect(reverse("create_listing"))
        
    return render(request, "auctions/new_category.html", {
        "form": NewCategoryForm()
    })


def listing(request, id):
    try:
        listing = Listing.objects.get(id=id)
    except:
        return render(request, "auctions/listing.html")

    try:
        is_on_watchlist = Watchlist.objects.get(user=request.user, listing=listing)
    except:
        is_on_watchlist = None

    try:
        comments = listing.comments.all()
    except:
        comments = None

    try:
        bid_count = listing.bids.all().count()
    except:
        bid_count = 0
    
    # If the listing has bids, check if the highest bid is the user's
    if bid_count > 0:
        highest_bid = listing.bids.all().order_by("value").last().value
        try:
            # Due to algorithm design, this query will only have one object 
            user_bid = Bid.objects.get(user=request.user, listing=listing).value
        except:
            user_bid = 0
        if user_bid == highest_bid: 
            user_bid_is_highest = True
        else:
            user_bid_is_highest = False
    else:
        user_bid_is_highest = False
        highest_bid = listing.starting_bid
        user_bid = 0

    invalid_bid_message = None
    if request.method == "POST":
        # Add/remove from watchlist
        if request.POST["option"] == "watchlist":
            if is_on_watchlist:
                is_on_watchlist.delete()
                is_on_watchlist = None
            else:
                is_on_watchlist = Watchlist(user=request.user, listing=listing)
                is_on_watchlist.save()
        # Place new bid
        elif request.POST["option"] == "bid" and listing.is_active:
            form = NewBidForm(request.POST)
            if form.is_valid() and listing.user != request.user:
                bid_value = form.cleaned_data["value"]
                # If listing has no bids and user's bid is at least equal to starting bid, than save
                if bid_count == 0 and bid_value >= listing.starting_bid:
                    bid = Bid(listing=listing, user=request.user, value=bid_value)
                    listing.starting_bid = bid_value
                    bid.save()
                    listing.save()
                    return HttpResponseRedirect(reverse("listing", kwargs={'id': listing.id}))
                # If listing has bids, the user's bid has to be greater than current bid, than SAVE user's new bid
                elif bid_value > highest_bid and user_bid == 0:
                    bid = Bid(listing=listing, user=request.user, value=bid_value)
                    listing.starting_bid = bid_value
                    bid.save()
                    listing.save()
                    return HttpResponseRedirect(reverse("listing", kwargs={'id': listing.id}))
                # If listing has bids, the user's bid has to be greater than current bid, than UPDATE user's current bid 
                elif bid_value > highest_bid:
                    bid = Bid.objects.get(user=request.user, listing=listing)
                    bid.value = bid_value
                    listing.starting_bid = bid_value
                    bid.save()
                    listing.save()
                    return HttpResponseRedirect(reverse("listing", kwargs={'id': listing.id}))
                else:
                    # Show invalid bid message
                    invalid_bid_message = "Bid must be equal or higher than the starting bid or higher than current bid."
        # Close auction
        elif request.POST["option"] == "close_auction":
            if listing.is_active:
                listing.is_active = False
                listing.save()
        # Add new comment
        elif request.POST["option"] == "comment":
            form = NewCommentForm(request.POST)
            if form.is_valid():
                text = form.cleaned_data["text"]
                comment = Comment(user=request.user, listing=listing, text=text)
                comment.save()
                return HttpResponseRedirect(reverse("listing", kwargs={'id': listing.id}))

    return render(request, "auctions/listing.html", {
        "listing":listing,
        "is_on_watchlist":is_on_watchlist,
        "comments":comments,
        "bid_count":bid_count,
        "user_bid_is_highest":user_bid_is_highest,
        "invalid_bid_message":invalid_bid_message,
        "bid_form":NewBidForm,
        "comment_form":NewCommentForm
    })


@login_required
def watchlist(request):
    try:
        watchlist = Watchlist.objects.all().filter(user=request.user)
    except:
        watchlist = None
        
    return render(request, "auctions/watchlist.html", {
        "watchlist":watchlist
    })

def categories(request):
    try:
        categories = Category.objects.all().order_by("name")
    except:
        categories = None

    return render(request, "auctions/categories.html", {
        "categories":categories
    })

def category(request, name):
    category = Category.objects.get(name=name)
    listings = category.listings.all()

    return render(request, "auctions/category.html", {
        "listings": listings,
        "name":name
    })