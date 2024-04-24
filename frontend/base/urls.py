from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("results", views.results, name="results"),
    path("about", views.about, name="about"),
    path("new-experiment", views.about, name="new-experiment"),
]
