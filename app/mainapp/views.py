import json
import os
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from mainapp.services.userManagement import UserManagement
from django.urls import reverse
from .forms import GroupForm
from .models import Group, UserMeta
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


def profilePage_view(request):
    context = {}
    return render(request, "profile.html", context)


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

@login_required(login_url='/login/')
def group_view(request):
    if request.method == "POST":
        form = GroupForm(request.POST, request.FILES)
        if form.is_valid():
            user_meta = UserMeta.objects.get(user=request.user)
            new_group = form.save(commit=False)
            new_group.owner = user_meta
            new_group.save()
            new_group.members.add(user_meta)
            return redirect('my-groups')
    else:
        form = GroupForm()

    return render(request, "create_group.html", {"form": form})


@login_required(login_url='/login/')
def my_groups_view(request):
    user_meta = UserMeta.objects.get(user=request.user)
    groups = Group.objects.filter(members=user_meta)
    return render(request, "my_groups.html", {"groups": groups})


@login_required(login_url='/login/')
def group_edit_view(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    user_meta = UserMeta.objects.get(user=request.user)

    if user_meta != group.owner:
        return redirect('my-groups')

    if request.method == 'POST':
        form = GroupForm(request.POST, request.FILES, instance=group)
        if form.is_valid():
            form.save()
            return redirect('my-groups')
    else:
        form = GroupForm(instance=group)

    return render(request, 'group_edit.html', {'form': form, 'group': group})


@login_required(login_url='/login/')
def delete_group(request, group_id):
    user_meta = UserMeta.objects.get(user=request.user)
    group = get_object_or_404(Group, id=group_id, owner=user_meta)

    if request.method == 'POST':
        group.delete()
        messages.success(request, 'Gruppe wurde gelöscht!')
        return redirect('my-groups')

    return redirect('group_settings')
