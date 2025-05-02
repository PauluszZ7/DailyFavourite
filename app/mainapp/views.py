from django.shortcuts import render

# Create your views here.


def mainPage_view(request):
    context = {}
    return render(request, "main.html", context) 

def loginPage_view(request):
    context = {}
    return render(request, "login.html", context)
