from datetime import datetime
import json
import os
import uuid

from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib import messages
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.exceptions import PermissionDenied

from mainapp.objects.dto_enums import DTOEnum
from mainapp.objects.enums import GenreEnum, RoleEnum
from mainapp.objects.exceptions import DailyFavouriteDBObjectNotFound
from mainapp.services.FriendsManagement import FriendsManagement
from mainapp.services.GroupManagement import GroupManagement
from mainapp.services.PostManagement import PostManagement
from mainapp.services.database import DatabaseManagement
from mainapp.services.spotifyConnector import SpotifyConnector
from django.views.decorators.http import require_GET

from mainapp.services.userManagement import UserManagement
from mainapp.objects.dtos import GroupDTO, PostDTO, UserDTO



# FRONTEND
@login_required
def homepage_view(request):
    posts = []

    user = UserManagement(request).getCurrentUser()
    try:
        friends_post = FriendsManagement(user).listPosts()
    except DailyFavouriteDBObjectNotFound:
        friends_post = []

    try:
        my_posts = PostManagement(user).listPosts(users=[user.id])
    except DailyFavouriteDBObjectNotFound:
        my_posts = []

    gm = GroupManagement(user)
    groups = gm.listGroupsWhereUserIsMember()

    if len(groups) > 0:
        for group in groups:
            try:
                p = gm.listPosts(group)
                posts.extend(p)
            except:
                continue

    posts.extend(my_posts)
    posts.extend(friends_post)
    posts = PostManagement(user).removeDuplicates(posts)
    posts = PostManagement(user).sortPosts(posts)
    posts = DTOEnum.POST.convertToJSON(posts)
    return render(request, 'homepage.html', {'posts': posts})


### Friends
@login_required
def friendsPage_view(request):
    user = UserManagement(request).getCurrentUser()

    friends = FriendsManagement(user).getFriends()
    
    users = []
    for friend in friends:
        users.append(DatabaseManagement(user).get(friend.friend, DTOEnum.USER))

    data = DTOEnum.USER.convertToJSON(users)
    return render(request, "friends.html", {"friends": data})

@login_required
def friends_search_view(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse({"error": "Fehlender Suchbegriff (q)"}, status=400)

    user = UserManagement(request).getCurrentUser()
    results = FriendsManagement(user).searchUsers(query)
    data = DTOEnum.USER.convertToJSON(results)
    return JsonResponse(data, safe=False)

@login_required
def friends_delete(request):
    print("Jetzt wurde der Freund gelöscht")


### Groups
@login_required
def my_groups_view(request):
    user = UserManagement(request).getCurrentUser()
    groups = GroupManagement(user).listGroupsWhereUserIsMember()
    return render(request, 'groups/my_groups.html', {'groups': groups})

@login_required
def create_group_view(request):
    user = UserManagement(request).getCurrentUser()

    if request.method == "POST":
        print("Neue Gruppe wird erstellt")
        name = request.POST.get("name")
        description = request.POST.get("description")
        is_public = bool(request.POST.get("is_public"))
        password = request.POST.get("password") or None
        genre = request.POST.get("genre")
        max_posts = int(request.POST.get("max_posts_per_day") or -1)
        post_permission = request.POST.get("post_permission") or RoleEnum.MEMBER
        read_permission = request.POST.get("read_permission") or RoleEnum.MEMBER
        profile_image = request.FILES.get("profile_Image") or None

        if profile_image:
            ext = profile_image.name.split('.')[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            relative_path = os.path.join("group_images", filename)
            full_path = os.path.join(settings.MEDIA_ROOT, relative_path)

            with default_storage.open(full_path, 'wb+') as destination:
                for chunk in profile_image.chunks():
                    destination.write(chunk)
        else:
            full_path = None

        group = GroupDTO(
            id = None,
            name = name,
            created_at = datetime.now(),
            description = description,
            profile_image = full_path,
            genre = genre,
            is_public = is_public,
            password = password,
            max_posts_per_day = max_posts,
            post_permission = post_permission,
            read_permission = read_permission,
            admin = user,
        )

        print("GROUP MACHT JETZT")
        GroupManagement(user).createGroup(group)
        return redirect("my-groups")

    context = {
        "genres": GenreEnum.get_values(),
        "permissions": RoleEnum.get_values(),
    }
    return render(request, "groups/create_group.html", context)


@login_required
def edit_group_view(request, group_id):
    user = UserManagement(request).getCurrentUser()
    try:
        group = DatabaseManagement(user).get(group_id, DTOEnum.GROUP)
    except DailyFavouriteDBObjectNotFound:
        raise Http404()

    if request.method == "POST" and isinstance(group, GroupDTO):
        name = request.POST.get("name")
        description = request.POST.get("description")
        is_public = bool(request.POST.get("is_public"))
        password = request.POST.get("password") or None
        genre = request.POST.get("genre")
        max_posts = int(request.POST.get("max_posts_per_day") or -1)
        post_permission = request.POST.get("post_permission") or RoleEnum.MEMBER
        read_permission = request.POST.get("read_permission") or RoleEnum.MEMBER
        profile_image = request.FILES.get("profile_Image") or None

        group.name = name
        group.description = description
        group.is_public = is_public
        if password is not None:
            group.password = password
        group.genre = genre
        group.max_posts_per_day = max_posts
        group.post_permission = post_permission
        group.read_permission = read_permission
        group.admin = DatabaseManagement(user).get(group.admin, DTOEnum.USER)

        try:
            GroupManagement(user).updateGroup(group)
        except PermissionError:
            raise PermissionDenied()

    context = {
        "genres": GenreEnum.get_values(),
        "permissions": RoleEnum.get_values(),
        "group": group,
    }

    return render(request, "groups/group_edit.html", context)

@login_required(login_url='/login/')
def delete_group_view(request, group_id):
    user = UserManagement(request).getCurrentUser()
    group = DatabaseManagement(user).get(group_id, DTOEnum.GROUP)

    if request.method == 'POST':
        GroupManagement(user).deleteGroup(group)
        messages.success(request, 'Gruppe wurde gelöscht!')
        return redirect('my-groups')

    messages.warning(request, 'Ungültige Anfrage.')
    return redirect('group-edit', group_id=group_id)

@login_required
def group_search_view(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse({"error": "Fehlender Suchbegriff (q)"}, status=400)

    user = UserManagement(request).getCurrentUser()
    results = GroupManagement(user).listGroups()
    
    data = []
    for group in results:
        if query.lower() in group.name.lower():
            data.append(
                {
                    "name": group.name,
                    "id": group.id,
                    "is_public": group.is_public,
                }
            )
    return JsonResponse(data, safe=False)

### POSTS
@login_required
def createPostPage_view(request):
    user = UserManagement(request).getCurrentUser()

    if request.method == "POST":
        # try:
            # JSON-Daten aus dem Request-Body lesen
            data = json.loads(request.body)
            group_id = data.get("group_id")
            music_id = data.get("music_id")

            # Theoretisch unmöglich jetzt in der Gruppe mit dem namen ___private___12345___ zu posten
            if group_id == "___private___12345___":
                group = None 
                print("Privater Post")
            else:
                group = DatabaseManagement(user).get(int(group_id), DTOEnum.GROUP)

            if music_id == "":
                JsonResponse({"success": False, "error": "Keinen validen Spotify Song ausgewählt."}, status=400)
            music = SpotifyConnector().get_Track(music_id)

            post = PostDTO(
                id=None,
                user=user,
                group=group,
                music=music,
                posted_at=datetime.now()
            )
            GroupManagement(user).createPost(post)
            return redirect("home")
        # except Exception as e:
        #     return JsonResponse({"success": False, "error": str(e)}, status=400)
    
    groups = GroupManagement(user).listGroupsWhereUserIsMember()

    return render(request, "create_post.html", {"groups": groups})

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
        user = UserManagement(request).getCurrentUser()
        # Sicherstellen, dass es die Archive Gruppe gibt
        GroupManagement(user)
        return JsonResponse({"redirect_url": reverse("home")})

    return JsonResponse({"error": "Nur POST erlaubt"}, status=405)

@login_required
def logout_view(request):
    UserManagement(request).logout()
    return redirect(reverse("home"))

@require_GET
@login_required
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
































































######  ALLES DARUNTER IGNORIEREN

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











def vote_view(request):
    return JsonResponse("Du hast gevoted.")
















