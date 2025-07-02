from datetime import datetime
import json
import os
import uuid

from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.exceptions import PermissionDenied

from mainapp.objects.dto_enums import DTOEnum
from mainapp.objects.enums import GenreEnum, RoleEnum
from mainapp.objects.exceptions import (
    DailyFavouriteDBObjectNotFound,
    DailyFavouriteMaxPostsPerDayReached,
    DailyFavouriteNoUserFound,
)
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
            except Exception:
                continue

    posts.extend(my_posts)
    posts.extend(friends_post)
    posts = PostManagement(user).removeDuplicates(posts)
    posts = PostManagement(user).sortPosts(posts)
    posts = PostManagement(user).convert_to_json(posts)
    return render(request, "homepage.html", {"posts": posts, "can_delete": False})


@login_required
def profilePage_view(request):
    user = UserManagement(request).getCurrentUser()
    return other_profilePage_view(request, user.id)


@login_required
def other_profilePage_view(request, id):
    cur_user = UserManagement(request).getCurrentUser()
    user = DatabaseManagement(cur_user).get(id, DTOEnum.USER)
    gm = GroupManagement(user)
    friend_combinations = FriendsManagement(cur_user).getFriends()
    is_following = False

    for combi in friend_combinations:
        if combi.friend == id:
            is_following = True
            break
    try:
        user_posts = gm.listPosts(gm.get_archive())
        user_posts = PostManagement(cur_user).sortPosts(user_posts)
        user_posts = PostManagement(cur_user).convert_to_json(user_posts)
    except Exception:
        user_posts = []

    if cur_user.id == user.id:
        can_delete = True
    else:
        can_delete = False

    context = {
        "profile_user": user,
        "posts": user_posts,
        "is_following": is_following,
        "can_delete": can_delete,
    }
    return render(request, "profile.html", context)


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
def friends_delete(request, id):
    user = UserManagement(request).getCurrentUser()
    friend = DatabaseManagement(user).get(id, DTOEnum.USER)
    FriendsManagement(user).removeFriend(friend)
    return redirect(request.META.get("HTTP_REFERER", "/"))


@login_required
def friends_add(request, id):
    user = UserManagement(request).getCurrentUser()
    friend = DatabaseManagement(user).get(id, DTOEnum.USER)
    FriendsManagement(user).addFriend(friend)
    return redirect(request.META.get("HTTP_REFERER", "/"))


### Groups
@login_required
def my_groups_view(request):
    user = UserManagement(request).getCurrentUser()
    groups = GroupManagement(user).listGroupsWhereUserIsMember()
    return render(request, "groups/my_groups.html", {"groups": groups})


@login_required
def groupFeed_view(request, id):
    user = UserManagement(request).getCurrentUser()
    group = DatabaseManagement(user).get(id, DTOEnum.GROUP)
    group.admin = DatabaseManagement(user).get(group.admin, DTOEnum.USER)
    try:
        posts = GroupManagement(user).listPosts(group)
        posts = PostManagement(user).sortPosts(posts)
        posts = PostManagement(user).convert_to_json(posts)
    except Exception:
        posts = []

    can_delete = False
    role = GroupManagement(user).get_role_for_group(group=group)
    if role == RoleEnum.ARCHIVE_VIEWER or role == RoleEnum.OWNER:
        can_delete = True
    elif (
        role == RoleEnum.MODERATOR
        and RoleEnum(RoleEnum.validate(group.post_permission)) != RoleEnum.OWNER
    ):
        can_delete = True
    context = {"posts": posts, "group": group, "can_delete": can_delete}
    return render(request, "feeds/group_feed.html", context)


@login_required
def create_group_view(request):
    user = UserManagement(request).getCurrentUser()

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        is_public = bool(request.POST.get("is_public"))
        password = request.POST.get("password") or None
        genre = request.POST.get("genre")
        max_posts = int(request.POST.get("max_posts_per_day") or -1)
        post_permission = request.POST.get("post_permission") or RoleEnum.MEMBER
        profile_image = request.FILES.get("profile_Image") or None

        if profile_image:
            ext = profile_image.name.split(".")[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            relative_path = os.path.join("group_images", filename)
            full_path = os.path.join(settings.MEDIA_ROOT, relative_path)

            with default_storage.open(full_path, "wb+") as destination:
                for chunk in profile_image.chunks():
                    destination.write(chunk)
        else:
            full_path = None

        group = GroupDTO(
            id=None,
            name=name,
            created_at=datetime.now(),
            description=description,
            profile_image=full_path,
            genre=genre,
            is_public=is_public,
            password=password,
            max_posts_per_day=max_posts,
            post_permission=post_permission,
            admin=user,
        )

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
        # profile_image = request.FILES.get("profile_Image") or None

        group.name = name
        group.description = description
        group.is_public = is_public
        if password is not None:
            group.password = password
        group.genre = genre
        group.max_posts_per_day = max_posts
        group.post_permission = post_permission
        group.admin = DatabaseManagement(user).get(group.admin, DTOEnum.USER)

        try:
            GroupManagement(user).updateGroup(group)
        except PermissionError:
            raise PermissionDenied()

        return redirect("my-groups")

    gm = GroupManagement(user)
    group_users = gm.getMembers(group)
    group_users = [
        {
            "id": user.id,
            "username": user.username,
            "role": gm.get_role_for_group(group=group, user=user).value,
        }
        for user in group_users
    ]
    context = {
        "genres": GenreEnum.get_values(),
        "permissions": RoleEnum.get_values(),
        "group": group,
        "group_users": group_users,
        "userPermission": GroupManagement(user).get_role_for_group(group=group).value,
    }

    return render(request, "groups/group_edit.html", context)


@login_required
def delete_group_view(request, group_id):
    user = UserManagement(request).getCurrentUser()
    group = DatabaseManagement(user).get(group_id, DTOEnum.GROUP)

    if request.method == "POST":
        GroupManagement(user).deleteGroup(group)
        messages.success(request, "Gruppe wurde gelöscht!")
        return redirect("my-groups")

    messages.warning(request, "Ungültige Anfrage.")
    return redirect("group-edit", group_id=group_id)


@login_required
def leave_group_view(request, group_id):
    user = UserManagement(request).getCurrentUser()
    group = DatabaseManagement(user).get(group_id, DTOEnum.GROUP)

    if request.method == "POST":
        try:
            GroupManagement(user).leaveGroup(group)
        except DailyFavouriteDBObjectNotFound:
            return JsonResponse(
                {"success": False, "error": "User ist nicht in der Gruppe."},
                status=500,
            )
        return redirect("my-groups")

    messages.warning(request, "Ungültige Anfrage.")
    return redirect("group-edit", group_id=group_id)


@login_required
def group_search_view(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse({"error": "Fehlender Suchbegriff (q)"}, status=400)

    user = UserManagement(request).getCurrentUser()
    results = GroupManagement(user).listGroups()
    already_joint = GroupManagement(user).listGroupsWhereUserIsMember()

    results = [result for result in results if result not in already_joint]

    print("Results: ", [result.name for result in results])

    if len(results) > 10:
        results = results[:10]

    data = []
    for group in results:
        if query.lower() in group.name.lower():
            data.append(
                {
                    "name": group.name,
                    "id": group.id,
                    "is_public": group.is_public,
                    "admin": DatabaseManagement(user)
                    .get(group.admin, DTOEnum.USER)
                    .username,
                }
            )
    return JsonResponse(data, safe=False)


### POSTS
@login_required
def createPostPage_view(request):
    user = UserManagement(request).getCurrentUser()

    if request.method == "POST":
        data = json.loads(request.body)
        group_id = data.get("group_id")
        music_id = data.get("music_id")

        # Theoretisch unmöglich jetzt in der Gruppe mit dem namen ___private___12345___ zu posten
        if group_id == "___private___12345___":
            group = None
        else:
            group = DatabaseManagement(user).get(int(group_id), DTOEnum.GROUP)

        if music_id == "":
            return JsonResponse(
                {"success": False, "error": "Keinen validen Spotify Song ausgewählt."},
                status=404,
            )
        music = SpotifyConnector().get_Track(music_id)

        post = PostDTO(
            id=None, user=user, group=group, music=music, posted_at=datetime.now()
        )
        try:
            GroupManagement(user).createPost(post)
        except DailyFavouriteMaxPostsPerDayReached:
            messages.error(
                request, "Maximale Posts für diesen Tag in der Gruppe aufgebraucht."
            )
            return JsonResponse(
                {
                    "success": False,
                    "error": "Maximale Posts für diesen Tag in der Gruppe aufgebraucht.",
                },
                status=403,
            )
        except PermissionError:
            messages.error(
                request,
                "Du hast keine Berechtigungen, um innerhalb der Gruppe Posten zu dürfen.",
            )
            return JsonResponse(
                {
                    "success": False,
                    "error": "Du hast keine Berechtigungen, um innerhalb der Gruppe Posten zu dürfen.",
                },
                status=403,
            )

        return JsonResponse({"success": True, "redirect_url": reverse("home")})

    groups = GroupManagement(user).listGroupsWhereUserIsMember()

    return render(request, "create_post.html", {"groups": groups})


@login_required
def delete_post_view(request, post_id):
    user = UserManagement(request).getCurrentUser()
    post = DatabaseManagement(user).get(post_id, DTOEnum.POST)
    if GroupManagement(user).get_role_for_group(post) == RoleEnum.ARCHIVE_VIEWER:
        # get Group Posts if exists
        posts = DatabaseManagement(user).list(user.id, DTOEnum.POST, "user_id")
        for p in posts:
            if (
                post.music == p.music
                and post.posted_at == p.posted_at
                and p.user == post.user
            ):
                PostManagement(user).deletePost(p)
    try:
        PostManagement(user).deletePost(post)
    except PermissionError:
        return JsonResponse(
            {
                "success": False,
                "error": "Keine Rechte um diesen Post löschen zu können.",
            },
            status=403,
        )

    return redirect(request.META.get("HTTP_REFERER", "/"))


def loginPage_view(request):
    context = {}
    return render(request, "login.html", context)


def registrationPage_view(request):
    context = {}
    return render(request, "registration.html", context)


@login_required
def comment_post_view(request, post_id):
    if request.method == "POST":
        comment = request.POST.get("comment") or None
        user = UserManagement(request).getCurrentUser()
        post = PostManagement(user).getPost(post_id)
        if comment is None or comment == "":
            return JsonResponse({"message": "Es wurde kein Kommentar übergeben."}, status=500)

        PostManagement(user).commentPost(post, comment)
        return JsonResponse({"message": "Kommentar erfolgreich erstellt."})

    return JsonResponse({"error": "Nur POST erlaubt"}, status=403)



# BACKEND
def registration_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")
        favorite_artist = data.get("favorite_artist")
        favorite_genre = data.get("favorite_genre")

        try:
            users = DatabaseManagement(None).list_all(DTOEnum.USER)
            names = [user.username for user in users]
            if username in names:
                return JsonResponse({"message": "Dieser Username ist schon vergeben!"}, status=500)
        except DailyFavouriteDBObjectNotFound:
            pass

        dto = UserDTO(
            id=None,
            username=username,
            profile_picture=None,
            favorite_artist=favorite_artist,
            favorite_genre=favorite_genre,
        )

        UserManagement(request).register(username, password, dto)
        return JsonResponse({"redirect_url": reverse("login")}, status=403)

    return JsonResponse({"error": "Nur POST erlaubt"}, status=403)


def login_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        try:
            UserManagement(request).login(username, password)
        except DailyFavouriteNoUserFound:
            return JsonResponse({"message": "Passwort und/oder Username stimmt nicht."})


        user = UserManagement(request).getCurrentUser()
        # Sicherstellen, dass es die Archive Gruppe gibt
        GroupManagement(user)
        return JsonResponse({"redirect_url": reverse("home")})

    return JsonResponse({"error": "Nur POST erlaubt"}, status=403)


@login_required
def join_group_view(request):
    # Exception Handling fehlt
    if request.method == "POST":
        id = request.POST.get("id", None)
        password = request.POST.get("password", None)

        user = UserManagement(request).getCurrentUser()
        group = DatabaseManagement(user).get(int(id), DTOEnum.GROUP)
        try:
            GroupManagement(user).joinGroup(group, password)
        except PermissionError:
            return JsonResponse({"message": "Incorrectes Passwort"}, status=403)
        return JsonResponse({"message": "user joint group"})

    return JsonResponse({"message": "wrong request type."})


@login_required
def remove_member_from_group_view(request, group_id):
    if request.method == "POST":
        user_id = request.POST.get("user_id", None)

        user = UserManagement(request).getCurrentUser()
        group = DatabaseManagement(user).get(int(group_id), DTOEnum.GROUP)
        remove_user = DatabaseManagement(user).get(user_id, DTOEnum.USER)
        try:
            GroupManagement(user).removeUserFromGroup(group, remove_user)
        except PermissionError as e:
            return JsonResponse({"message": str(e)}, status=403)
        return JsonResponse({"message": "User entfernt"})

    return JsonResponse({"message": "wrong request type."})


@login_required
def update_user_role_view(request, group_id):
    if request.method == "POST":
        user_id = request.POST.get("user_id", None)
        role = request.POST.get("role", None)

        if user_id is None or role is None:
            return JsonResponse({"message": "Critical Data needed."})

        user = UserManagement(request).getCurrentUser()
        group = DatabaseManagement(user).get(int(group_id), DTOEnum.GROUP)
        update_user = DatabaseManagement(user).get(user_id, DTOEnum.USER)
        try:
            GroupManagement(user).changeUserRole(
                group, update_user, role=RoleEnum(RoleEnum.validate(role))
            )
        except PermissionError as e:
            return JsonResponse({"message": str(e)}, status=403)
        return JsonResponse({"message": "User entfernt"})

    return JsonResponse({"message": "wrong request type."})


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


@login_required
def vote_view(request, post_id: int, vote_type: str):
    user = UserManagement(request).getCurrentUser()
    post = DatabaseManagement(user).get(post_id, DTOEnum.POST)

    if vote_type == "up":
        PostManagement(user).upvotePost(post)
    elif vote_type == "down":
        PostManagement(user).downVotePost(post)
    else:
        return JsonResponse({"error": "invalid vote type"}, status=500)
    return redirect(request.META.get("HTTP_REFERER", "/"))
