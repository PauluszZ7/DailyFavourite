import json
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login


def basenavPage_view(request):
    context = {}
    return render(request, "base.html", context)


def mainPage_view(request):
    context = {}
    return render(request, "main.html", context)


def loginPage_view(request):
    context = {}
    return render(request, "login.html", context)


def registrationPage_view(request):
    context = {}
    return render(request, "registration.html", context)


def register_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        print("Neuer Benutzername:", username)
        return JsonResponse({"message": "Empfangen"}, status=200)
    return JsonResponse({"error": "Nur POST erlaubt"}, status=400)


def api_login_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"message": "Login erfolgreich"}, status=200)
        else:
            return JsonResponse({"message": "Login fehlgeschlagen"}, status=401)

    return JsonResponse({"error": "Nur POST erlaubt"}, status=405)


def mainfeedPage_view(request):
    context = {}
    return render(request, "mainfeed.html", context)


def profilePage_view(request):
    context = {}
    return render(request, "profile.html", context)


def favouritePage_view(request):
    context = {}
    return render(request, "favourites.html", context)
