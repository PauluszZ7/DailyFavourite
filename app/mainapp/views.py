import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from mainapp.services.userManagement import UserManagement
from mainapp.services.database import create_or_update_track
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from mainapp.services.serializers import ImportTrackSerializer
from mainapp.services.spotifyConnector import (
    fetch_spotify_track,
    SpotifyTrackNotFoundException,
)


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


def basenavPage_view(request):
    context = {}
    return render(request, "base.html", context)

def testimport_view(request):
    context = {}
    return render(request, "testimport.html", context)


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


class ImportTrackView(APIView):

    def post(self, request):
        serializer = ImportTrackSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        track_id = serializer.validated_data["spotify_track_id"]

        try:
            track_data = fetch_spotify_track(track_id)

            create_or_update_track(track_data)

            return Response(
                {"detail": "Track importiert."}, status=status.HTTP_201_CREATED
            )

        except SpotifyTrackNotFoundException as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response(
                {"detail": "Interner Serverfehler."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
