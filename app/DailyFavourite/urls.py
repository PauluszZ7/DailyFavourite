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
from django.urls import path
from mainapp.views import (
    mainPage_view,
    loginPage_view,
    registrationPage_view,
    mainfeedPage_view,
    profilePage_view,
    favouritePage_view,
    friendsPage_view,
    homepageFeed_view,
    groupFeed_view,
    friendsFeed_view,
    login_view,
    registration_view,
    logout_view,
    vote_view,
    create_group_view,
    my_groups_view,
    edit_group_view,
    delete_group_view,
    homepage_view,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", homepage_view, name="home"),
    path("login/", loginPage_view, name="login"),
    path("registration/", registrationPage_view, name="registration"),
    path("mainfeed/", mainfeedPage_view, name="mainfeed"),
    path("profile/", profilePage_view, name="profile"),
    path("favourites/", favouritePage_view, name="favourite"),
    path("homepage/", homepageFeed_view, name="homepage"),
    path("groupfeed/", groupFeed_view, name="groupfeed"),
    path("friends/", friendsPage_view, name="friends"),
    path("friendsfeed/", friendsFeed_view, name="friendsfeed"),
    path("api/login/", login_view, name="backend-login"),
    path("api/logout/", logout_view, name="backend-logout"),
    path("api/registration/", registration_view, name="backend-registration"),
    path("api/vote/<int:post_id>/<str:vote_type>/", vote_view, name="vote"),
    path('groups/create/', create_group_view, name='group-create'),
    path('groups/', my_groups_view, name='my-groups'),
    path('groups/<int:group_id>/edit/', edit_group_view, name='group-edit'),
    path('groups/<int:group_id>/delete/', delete_group_view, name='delete_group'),
]
