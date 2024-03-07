from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from network.models import *

from .models import User


def index(request):
    posts = Post.objects.all().order_by('-date')
    return render(request, "network/index.html", {
        "posts": posts,
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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def new_post(request):
    if request.method == "POST":
        content = request.POST["content"]
        post = Post(user=request.user, content=content)
        post.save()
    
    return HttpResponseRedirect(reverse("index"))


def profile(request, username):
    profile_user = User.objects.get(username=username)
    if request.method == "POST":
        if request.POST["follow"] == "Follow":
            follow = Follow(followed=profile_user, follower=request.user)
            follow.save()
        else:
            follow = Follow.objects.get(followed=profile_user, follower=request.user)
            follow.delete()

    posts = Post.objects.all().filter(user=profile_user).order_by('-date')
    logged_user = None
    follows = False
    if request.user.is_authenticated:
        logged_user = request.user
        try:
            if Follow.objects.get(followed=profile_user, follower=logged_user):
                follows = True
        except:
            pass

    return render(request, "network/profile.html", {
        "profile_user": profile_user,
        "posts": posts,
        "logged_user": logged_user,
        "follows": follows
    })


@login_required
def following(request):
    try:
        followed_users = User.objects.filter(followers__follower=request.user)
    except:
        followed_users = None
    
    try:
        posts = Post.objects.all().filter(user__in=followed_users).order_by('-date')
    except:
        posts = None

    return render(request, "network/following.html", {
        "posts": posts,
    })