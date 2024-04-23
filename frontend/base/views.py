from django.shortcuts import render


def home(request):
    context = {"title": "asf"}
    return render(request, "base/home.html", context)
