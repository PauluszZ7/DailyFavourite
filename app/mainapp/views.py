import json
import os
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from mainapp.services.userManagement import UserManagement
from .models import Group, UserMeta
from django.utils import timezone
from django.contrib import messages


# FRONTEND
@login_required
def mainPage_view(request):
    user = UserManagement(request).getCurrentUser()
    context = {"username": user.username}
    return render(request, "main.html", context)


def loginPage_view(request):
    context = {}
    return render(request, "login.html", context)


def registrationPage_view(request):
    context = {}
    return render(request, "registration.html", context)


def mainfeedPage_view(request):
    context = {}
    return render(request, "mainfeed.html", context)


def favouritePage_view(request):
    context = {}
    return render(request, "favourites.html", context)


def homepageFeed_view(request):
    json_path = os.path.join(os.path.dirname(__file__), "objects/test_posts.json")

    with open(json_path, "r", encoding="utf-8") as f:
        posts_data = json.load(f)

    context = {"posts": posts_data}
    return render(request, "feeds/homepage_feed.html", context)


def groupFeed_view(request):
    json_path = os.path.join(os.path.dirname(__file__), "objects/test_posts.json")

    with open(json_path, "r", encoding="utf-8") as f:
        posts_data = json.load(f)

    context = {"posts": posts_data}
    return render(request, "feeds/group_feed.html", context)


def friendsFeed_view(request):
    json_path = os.path.join(os.path.dirname(__file__), "objects/test_posts.json")

    with open(json_path, "r", encoding="utf-8") as f:
        posts_data = json.load(f)

    context = {"posts": posts_data}
    return render(request, "feeds/friends_feed.html", context)

@login_required
def profilePage_view(request):
    user = UserManagement(request).getCurrentUser()

    json_path = os.path.join(os.path.dirname(__file__), "objects/test_posts.json")
    with open(json_path, "r", encoding="utf-8") as f:
        posts_data = json.load(f)

    user_posts = [post for post in posts_data if post["user"]["id"] == user.id]

    context = {
        "user": user,
        "user_posts": user_posts
    }
    return render(request, "profile.html", context)


# BACKEND
def registration_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        UserManagement(request).register(username, password)
        return JsonResponse({"redirect_url": reverse("login")})

    return JsonResponse({"error": "Nur POST erlaubt"}, status=400)


def login_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        UserManagement(request).login(username, password)
        return JsonResponse({"redirect_url": reverse("home")})

    return JsonResponse({"error": "Nur POST erlaubt"}, status=405)


def logout_view(request):
    UserManagement(request).logout()
    return redirect(reverse("home"))

def vote_view(request):
    return JsonResponse("Du hast gevoted.")


def friendsPage_view(request):
    return render(request, "friends.html")


@login_required
def create_group_view(request):
    user_meta = UserMeta.objects.get(id=request.user.id)

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        is_public = bool(request.POST.get("is_public"))
        genre = request.POST.get("genre") or None
        max_posts = int(request.POST.get("max_posts_per_day") or 1)
        post_permission = request.POST.get("post_permission")
        read_permission = request.POST.get("read_permission")
        profile_image = request.FILES.get("profile_Image")

        group = Group.objects.create(
            name=name,
            description=description,
            is_public=is_public,
            genre=genre,
            max_posts_per_day=max_posts,
            post_permission=post_permission,
            read_permission=read_permission,
            profile_Image=profile_image,
            owner=user_meta,
            created_at=timezone.now(),
        )
        group.members.add(user_meta)
        group.moderators.add(user_meta)

        return redirect("my-groups")

    return render(request, "groups/create_group.html", {"group": Group()})


@login_required
def edit_group_view(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    user_meta = UserMeta.objects.get(id=request.user.id)

    if request.method == "POST":
        group.name = request.POST.get("name")
        group.description = request.POST.get("description")
        group.is_public = request.POST.get("is_public") == "True"
        group.genre = request.POST.get("genre") or None
        group.max_posts_per_day = int(request.POST.get("max_posts_per_day") or 1)
        group.post_permission = request.POST.get("post_permission")
        group.read_permission = request.POST.get("read_permission")

        if "profile_Image" in request.FILES:
            group.profile_Image = request.FILES["profile_Image"]

        group.save()
        return redirect("my-groups", group_id=group.id)

    return render(request, "groups/group_edit.html", {"group": group})


@login_required
def my_groups_view(request):
    user_meta = UserMeta.objects.get(id=request.user.id)
    groups = Group.objects.filter(members=user_meta) if user_meta else []
    return render(request, 'groups/my_groups.html', {'groups': groups})


@login_required(login_url='/login/')
def delete_group_view(request, group_id):
    try:
        user_meta = UserMeta.objects.get(id=request.user.id)
    except UserMeta.DoesNotExist:
        messages.error(request, 'Benutzerprofil nicht gefunden.')
        return redirect('my-groups')

    group = get_object_or_404(Group, id=group_id, owner=user_meta)

    if request.method == 'POST':
        group.delete()
        messages.success(request, 'Gruppe wurde gelöscht!')
        return redirect('my-groups')

    # Optional: Rückleitung, falls DELETE ohne POST aufgerufen wird
    messages.warning(request, 'Ungültige Anfrage.')
    return redirect('group-edit', group_id=group_id)