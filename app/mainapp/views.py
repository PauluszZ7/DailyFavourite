import json
import os

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from mainapp.services.spotifyConnector import SpotifyConnector
from django.views.decorators.http import require_GET

from mainapp.services.userManagement import UserManagement
from mainapp.objects.dtos import UserDTO

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

    context = {"user": user, "user_posts": user_posts}
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
    return render(
        request,
        "create_post.html",
        {
            "groups": groups.values(),
            "musics": musics.values(),
        },
    )


def friendsPage_view(request):
    return render(request, "friends.html")


# BACKEND
def registration_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")
        favorite_artist = data.get("favorite_artist")
        favorite_genre = data.get("favorite_genre")

        dto = UserDTO(
            id=None,
            username=username,
            profile_picture=None,
            favorite_artist=favorite_artist,
            favorite_genre=favorite_genre,
        )

        UserManagement(request).register(username, password, dto)
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
    # user_meta = UserMeta.objects.get(id=request.user.id)

    # if request.method == "POST":
    #     name = request.POST.get("name")
    #     description = request.POST.get("description")
    #     is_public = bool(request.POST.get("is_public"))
    #     genre = request.POST.get("genre") or None
    #     max_posts = int(request.POST.get("max_posts_per_day") or -1)
    #     post_permission = request.POST.get("post_permission") or RoleEnum.MEMBER
    #     read_permission = request.POST.get("read_permission") or RoleEnum.MEMBER
    #     profile_image = request.FILES.get("profile_Image")
    #     print(profile_image)

        # group = Group.objects.create(
        #     name=name,
        #     description=description,
        #     is_public=is_public,
        #     genre=genre,
        #     max_posts_per_day=max_posts,
        #     post_permission=post_permission,
        #     read_permission=read_permission,
        #     profile_Image=profile_image,
        #     owner=user_meta,
        #     created_at=timezone.now(),
        # )
        # group.members.add(user_meta)
        # group.moderators.add(user_meta)

        return redirect("my-groups")

    # return render(request, "groups/create_group.html", {"group": Group()})


@login_required
def edit_group_view(request, group_id):
    # group = get_object_or_404(Group, id=group_id)

    # if request.method == "POST":
    #     group.name = request.POST.get("name")
    #     group.description = request.POST.get("description")
    #     group.is_public = request.POST.get("is_public") == "True"
    #     group.genre = request.POST.get("genre") or None
    #     group.max_posts_per_day = int(request.POST.get("max_posts_per_day") or 1)
    #     group.post_permission = request.POST.get("post_permission")
    #     group.read_permission = request.POST.get("read_permission")

    #     if "profile_Image" in request.FILES:
    #         group.profile_Image = request.FILES["profile_Image"]

    #     group.save()
    #     return redirect("my-groups", group_id=group.id)

    return render(request, "groups/group_edit.html", {"group": group})


@login_required
def my_groups_view(request):
    # user_meta = UserMeta.objects.get(id=request.user.id)
    # groups = Group.objects.filter(members=user_meta) if user_meta else []
    groups = []
    return render(request, 'groups/my_groups.html', {'groups': groups})


@login_required(login_url='/login/')
def delete_group_view(request, group_id):
    # try:
    #     user_meta = UserMeta.objects.get(id=request.user.id)
    # except UserMeta.DoesNotExist:
    #     messages.error(request, 'Benutzerprofil nicht gefunden.')
    #     return redirect('my-groups')

    # group = get_object_or_404(Group, id=group_id, owner=user_meta)

    # if request.method == 'POST':
    #     group.delete()
    #     messages.success(request, 'Gruppe wurde gelöscht!')
    #     return redirect('my-groups')

    # messages.warning(request, 'Ungültige Anfrage.')
    # return redirect('group-edit', group_id=group_id)
    return redirect('my-groups')


def homepage_view(request):
    json_path = os.path.join(os.path.dirname(__file__), 'test_posts.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        posts = json.load(f)

    return render(request, 'homepage.html', {'posts': posts})

@require_GET
def spotify_search_view(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse({"error": "Fehlender Suchbegriff (q)"}, status=400)

    try:
        spotify = SpotifyConnector()
        results = spotify.search_music_title(query, max_results=5)
        return JsonResponse(results, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
