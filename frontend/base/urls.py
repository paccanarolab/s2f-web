from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("results", views.results, name="results"),
    path("about", views.about, name="about"),
    path("job/<token>", views.job, name="job"),
    path("search", views.job_search, name="search"),
    path("new-experiment", views.add_job, name="new-experiment"),
    path("api/ping", views.ping, name="api-ping"),
    path("api/pending_jobs", views.pending_jobs, name="api-pending-jobs"),
    path("api/update_job_status",
         views.job_update_status,
         name="api-update-job-status"),
    path("api/update_job_result",
         views.job_update_result,
         name="api-update-job-result"),
    path("api/job_details/<token>", views.job_details, name="api-job-details"),
    path("api/job_fasta/<token>", views.job_fasta, name="api-job-fasta"),
    path("api/job_annot/<token>", views.job_annot, name="api-job-annot"),
]
