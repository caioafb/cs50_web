from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from network.models import *

from .models import User

def index(request):
    posts = Post.objects.all().order_by('-date')
    post_paginator = Paginator(posts, 10)
    page_num = request.GET.get('page')
    page = post_paginator.get_page(page_num)
    iterator = range(1,page.paginator.num_pages+1)
    max_page = max(iterator)

    return render(request, "network/index.html", {
        "page": page,
        "iterator": iterator,
        "max_page": max_page
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
        if request.POST["id"] == "0":
            post = Post(user=request.user, content=request.POST["content"])
            post.save()
        else:
            # Edit post
            edited_post = Post.objects.get(id=request.POST["id"])
            edited_post.content = request.POST["content"]
            edited_post.save()
    
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
        post_paginator = Paginator(posts, 10)
        page_num = request.GET.get('page')
        page = post_paginator.get_page(page_num)
        iterator = range(1,page.paginator.num_pages+1)
        max_page = max(iterator)
    except:
        page = None

    return render(request, "network/following.html", {
        "page": page,
        "iterator": iterator,
        "max_page": max_page
    })

@csrf_exempt
@login_required
def update_likes(request, post_id):

    # Query for requested post
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Return post like amount
    if request.method == "GET":
        print(post.likes.count())
        return JsonResponse({"likes": post.likes.count()})

    # Update like count
    elif request.method == "PUT":
        try:
            like = Like.objects.get(user=request.user, post=post_id)
        except:
            like = None

        if like:
            like.delete()
        else:
            like = Like(user=request.user, post=post)
            like.save()
        
        return HttpResponse(status=204)

    # Post must be via GET or PUT
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)