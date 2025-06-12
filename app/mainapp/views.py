import json
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .forms import GroupForm
from .models import Group
from django.contrib import messages

from mainapp.services.userManagement import UserManagement
from django.contrib.auth.decorators import login_required



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


@login_required(login_url='/login/')
def group_view(request):
    if request.method == "POST":
        form = GroupForm(request.POST, request.FILES)
        if form.is_valid():
            new_group = form.save(commit=False)
            new_group.owner = request.user
            new_group.save()
            new_group.members.add(request.user)
            new_group.save()
            return redirect('my-groups')
    else:
        form = GroupForm()

    return render(request, "create_group.html", {"form": form})

@login_required(login_url='/login/')
def my_groups_view(request):
    user = request.user
    groups = Group.objects.filter(members=user)
    return render(request, "my_groups.html", {"groups": groups})


@login_required(login_url='/login/')
def group_edit_view(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.user != group.owner:
        return redirect('my-groups')

    if request.method == 'POST':
        form = GroupForm(request.POST, request.FILES, instance=group)
        if form.is_valid():
            form.save()
            return redirect('my-groups')
    else:
        form = GroupForm(instance=group)

    return render(request, 'group_edit.html', {'form': form, 'group': group})


@login_required
def delete_group(request, group_id):
    group = get_object_or_404(Group, id=group_id, owner=request.user)

    if request.method == 'POST':
        group.delete()
        messages.success(request, 'Gruppe wurde gelöscht!')
        return redirect('my-groups')

    return redirect('group_settings')
