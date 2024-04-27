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
    path("api/update_job_status", views.job_update, name="api-update-job"),
    path("api/job_files/<token>", views.job_files, name="api-job-files"),
    path("api/job_fasta/<token>", views.job_fasta, name="api-job-fasta"),
    path("api/job_annot/<token>", views.job_annot, name="api-job-annot"),
]
