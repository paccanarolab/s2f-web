from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("results", views.results, name="results"),
    path("about", views.about, name="about"),
    path("job/<token>", views.job, name="job"),
    path("search", views.job_search, name="search"),
    path("new-experiment", views.add_job, name="new-experiment"),
    path("api/pending_jobs", views.pending_jobs, name="api-pending-jobs"),
    path("api/update_job_status", views.job_update, name="api-update-job"),
]
