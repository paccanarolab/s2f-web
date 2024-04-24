from django.shortcuts import render


def home(request):
    context = {"active": "home"}
    return render(request, "base/home.html", context)


def results(request):
    context = {"active": "results"}
    return render(request, "base/home.html", context)


def about(request):
    context = {"active": "about"}
    return render(request, "base/about.html", context)
