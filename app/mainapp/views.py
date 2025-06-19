import json
import os
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from mainapp.services.userManagement import UserManagement
from django.views.decorators.csrf import csrf_exempt


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

@csrf_exempt  # (temporär CSRF-Schutz deaktiviert – nur für Debugging-Zwecke)
def createPostPage_view(request):
    # Lade JSON-Daten aus der Datei
    json_path = os.path.join(os.path.dirname(__file__), "objects/test_posts.json")
    with open(json_path, "r", encoding="utf-8") as f:
        posts_data = json.load(f)

    # Extrahiere eindeutige Gruppen und Musikstücke aus den Posts
    groups = {post["group"]["id"]: post["group"] for post in posts_data}
    musics = {post["music"]["id"]: post["music"] for post in posts_data}

    if request.method == "POST":
        try:
            # JSON-Daten aus dem Request-Body lesen
            data = json.loads(request.body)
            group_id = data.get("group_id")
            music_id = data.get("music_id")
            print("Empfangene Daten:", group_id, music_id)

            # Erfolgsmeldung zurückgeben
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    # Bei GET einfach das Template anzeigen
    return render(request, "create_post.html", {
        "groups": groups.values(),
        "musics": musics.values(),
    })

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
