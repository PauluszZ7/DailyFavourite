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
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", homepage_view, name="home"),  # DONE
    path("login/", loginPage_view, name="login"),  # DONE
    path("registration/", registrationPage_view, name="registration"),  # DONE
    path("profile/", profilePage_view, name="profile"),  # FAST DONE (PROFILBILD)
    path(
        "profile/<int:id>/", other_profilePage_view, name="other-profile"
    ),  # FAST DONE (PROFILBILD)
    path("friends/", friendsPage_view, name="friends"),  # FAST DONE (PROFIL FEHLT)
    path("friends/search/", friends_search_view, name="friends-search"),  # DONE
    path("friends/delete/<int:id>/", friends_delete, name="friends-delete"),  # DONE
    path("friends/add/<int:id>/", friends_add, name="friends-delete"),  # DONE
    path("post/create/", createPostPage_view, name="create-post"),  # DONE
    path("groups/create/", create_group_view, name="group-create"),  # DONE
    path("groups/", my_groups_view, name="my-groups"),  # FAST DONE (PROFILBILD)
    path(
        "groups/join/", join_group_view, name="group-join"
    ),  # FAST DONE (PRIVATE JOIN GEHT NICHT)
    path("groups/<int:id>/", groupFeed_view, name="group-feed"),  # DONE
    path(
        "groups/<int:group_id>/edit/", edit_group_view, name="group-edit"
    ),  # FAST DONE (PROFILBILD)
    path(
        "groups/<int:group_id>/delete/", delete_group_view, name="delete_group"
    ),  # DONE
    path("api/login/", login_view, name="backend-login"),  # DONE
    path("api/logout/", logout_view, name="backend-logout"),  # DONE
    path("api/registration/", registration_view, name="backend-registration"),  # DONE
    path("api/vote/<int:post_id>/<str:vote_type>/", vote_view, name="vote"),  # DONE
    path("api/search/spotify/", spotify_search_view, name="spotify-search"),  # DONE
    path("api/search/group/", group_search_view, name="group-search"),  # DONE
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
