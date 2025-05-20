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
    api_login_view,
    basenavPage_view,
    mainfeedPage_view,
    profilePage_view,
    favouritePage_view,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", mainPage_view, name="home"),
    path("login/", loginPage_view, name="login"),
    path("registration/", registrationPage_view, name="registration"),
    path("api/login/", api_login_view, name="api-login"),
    path("base/", basenavPage_view, name="basenav"),
    path("mainfeed/", mainfeedPage_view, name="mainfeed"),
    path("profile/", profilePage_view, name="profile"),
    path("favourites/", favouritePage_view, name="favourite"),
]
