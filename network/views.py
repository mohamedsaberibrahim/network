import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.defaulttags import register
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView

from .models import User, Post, Like

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['body']

        labels = {
            'body': ''
        }

@register.filter
def get_range(value):
    return range(1, value + 1)

@register.filter
def likes(user, likes):
    for like in likes:
        if like.user == user:
            return True
    return False


def index(request):
    
    posts = Post.objects.all().order_by("-timestamp")
    paginator = Paginator(posts, 10) # Show 10 contacts per page.
    page_number = request.GET.get('page')
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, "network/index.html", {
        "posts" : posts
    })

def getposts(request, posts):

    if posts == "all":
        posts = Post.objects.all()
    elif posts == "following":
        posts = Post.objects.filter(user__in=request.user.following.all())
    else:
        return JsonResponse({"error": "Invalid choice."}, status=400)
    
    
    posts = posts.order_by("-timestamp").all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page_number')

    # Return emails in reverse chronologial order
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return JsonResponse({"posts": [post.serialize() for post in page_obj.object_list]
    }, safe=False)

@csrf_exempt
def addpost(request):
    # Composing a new email must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Get body of post
    data = json.loads(request.body)
    body = data.get("body", "")

    # Create new post
    post = Post(
        user=request.user, 
        body=body,
        likeCount=0
        )
    post.save()

    return JsonResponse({"message": "Post added successfully."}, status=201)

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

def profile(request, profile_id):
    profileuser = User.objects.get(pk=profile_id)
    print(profileuser, profileuser.following.all())
    return render(request, "network/profile.html", {
        "posts" : profileuser.posts.all().order_by("-timestamp"),
        "user_data" : {
            "user": profileuser, 
            "following" : profileuser.following.count(),
            "followers" : profileuser.followers.count()
        }
    })

def follow(request, profile_id):
    current_user = request.user
    
    if request.method == "POST":
        if request.POST["_method"] == "PUT":
            current_user.following.add(User.objects.get(id=profile_id))
        elif request.POST["_method"] == "DELETE":
            current_user.following.remove(User.objects.get(id=profile_id))
    
    return HttpResponseRedirect(reverse("profile", kwargs={"profile_id": profile_id}))


def following(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            body =  form.cleaned_data["body"]
            post = Post(user=request.user, body=body)
            post.save()
    posts = Post.objects.filter(user__in=request.user.following.all()).order_by("-timestamp")
    paginator = Paginator(posts, 10) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, "network/index.html", {
        "postForm" : PostForm(),
        "posts" : posts
    })

@csrf_exempt
def edit(request, post_id):

    # Query for requested post
    try:
        post = Post.objects.get(user=request.user, pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse( {"error": "Post not found."}, status=404)

    # Update post body
    if request.method == "PUT":
        data = json.loads(request.body)
        if data.get("body") is not None:
            post.body = data["body"]
        post.save()
        return HttpResponse(status=204)

    # Email must be via GET or PUT
    else:
        return JsonResponse({
            "error": "PUT request required."
        }, status=400)

@csrf_exempt
def like(request, post_id):

    # Query for requested post
    try:
        post = Post.objects.get(user=request.user, pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse( {"error": "Post not found."}, status=404)

    # Update post like & unlike Count, Create a new Like
    if request.method == "PUT":
        like = Like(
        user=request.user,
        post=post)

        like.save()
        post.likeCount = post.likeCount + 1
        post.save()
        like_id = like.id
        print(like_id)
        return JsonResponse(
            {
                "like_id": like_id
            }, status=201)
    elif request.method == "DELETE":
        data = json.loads(request.body)
        if data.get("like") is not None:
            like_id = data.get("like")
            Like.objects.get(pk=like_id).delete()
            print("Hello")
            post.likeCount = post.likeCount - 1
        post.save()
        return HttpResponse(status=204)

    # Post must be PUT
    else:
        return JsonResponse({
            "error": "PUT request required."
        }, status=400)


def post(request, post_id):

    # Query for requested email
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Return email contents
    if request.method == "GET":
        return JsonResponse(post.serialize())
