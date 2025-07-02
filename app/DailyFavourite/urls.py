"""
URL configuration for DailyFavourite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from mainapp.views import (
    loginPage_view,
    registrationPage_view,
    profilePage_view,
    other_profilePage_view,
    friendsPage_view,
    createPostPage_view,
    groupFeed_view,
    login_view,
    registration_view,
    logout_view,
    vote_view,
    create_group_view,
    my_groups_view,
    edit_group_view,
    delete_group_view,
    homepage_view,
    spotify_search_view,
    friends_search_view,
    friends_delete,
    friends_add,
    group_search_view,
    join_group_view,
    leave_group_view,
    remove_member_from_group_view,
    update_user_role_view,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", homepage_view, name="home"),
    path("login/", loginPage_view, name="login"),
    path("registration/", registrationPage_view, name="registration"),
    path("profile/", profilePage_view, name="profile"),
    path(
        "profile/<int:id>/", other_profilePage_view, name="other-profile"
    ),
    path("friends/", friendsPage_view, name="friends"),
    path("friends/search/", friends_search_view, name="friends-search"),
    path("friends/delete/<int:id>/", friends_delete, name="friends-delete"),
    path("friends/add/<int:id>/", friends_add, name="friends-delete"),
    path("post/create/", createPostPage_view, name="create-post"),
    path("groups/create/", create_group_view, name="group-create"),
    path("groups/", my_groups_view, name="my-groups"),
    path(
        "groups/join/", join_group_view, name="group-join"
    ),
    path("groups/<int:id>/", groupFeed_view, name="group-feed"),
    path(
        "groups/<int:group_id>/edit/", edit_group_view, name="group-edit"
    ),
    path("groups/<int:group_id>/leave/", leave_group_view, name="group-leave"),
    path("groups/<int:group_id>/remove-user/", remove_member_from_group_view, name="group-remove"),
    path("groups/<int:group_id>/update-user/", update_user_role_view, name="group-update"),
    path(
        "groups/<int:group_id>/delete/", delete_group_view, name="delete_group"
    ),
    path("api/login/", login_view, name="backend-login"),
    path("api/logout/", logout_view, name="backend-logout"),
    path("api/registration/", registration_view, name="backend-registration"),
    path("api/vote/<int:post_id>/<str:vote_type>/", vote_view, name="vote"),
    path("api/search/spotify/", spotify_search_view, name="spotify-search"),
    path("api/search/group/", group_search_view, name="group-search"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
