from django.shortcuts import render, redirect, get_object_or_404
from django.http import (HttpResponseBadRequest, HttpResponse, JsonResponse,
                         StreamingHttpResponse)
from django.conf import settings
from email_validator import validate_email, EmailNotValidError
from slugify import slugify
from base.validators import fasta_validator, annotation_validator
from base.models import Job, JobEvent, Status
from base.services import handle_upload, file_iterator
from datetime import datetime
from pathlib import Path
from oauth2_provider.decorators import rw_protected_resource
from django.views.decorators.csrf import csrf_exempt
import logging
from base.mail import send_email, EMAIL_TEMPLATES


log = logging.getLogger("main")


STATIC_ROOT = Path(settings.STATIC_ROOT)
MEDIA_ROOT = Path(settings.MEDIA_ROOT)


def home(request):
    context = {"active": "home"}
    return render(request, "base/home.html", context)


def add_job(request):
    if request.method == "POST":
        alias = slugify(request.POST["alias"])
        try:
            validation = validate_email(request.POST["email"])
            email = validation.email
        except EmailNotValidError:
            email = "noemail@noemail.com"
            # response = HttpResponseBadRequest()
            # response.write(e)
            # return response
        creation_dt = datetime.now()
        creation_str = creation_dt.strftime('%Y_%m_%d-%H_%M_%S')
        upload_dir = MEDIA_ROOT / f"{creation_str}-{alias}"
        upload_dir.mkdir()
        base_name = f"{creation_str}-{alias}"

        if "fasta-file" in request.FILES:
            fasta_file = request.FILES["fasta-file"]
            fasta_path = upload_dir / f"{base_name}.fasta"
            handle_upload(fasta_file, fasta_path)
            fasta_validation = fasta_validator(fasta_path)
            if fasta_validation["status"] != "valid":
                response = HttpResponseBadRequest()
                response.write(fasta_validation["message"])
                return response
        else:
            response = HttpResponseBadRequest()
            response.write("A FASTA file is mandatory")
            return response

        annotation_path = ""
        if "annotation-file" in request.FILES:
            annotation_file = request.FILES["annotation-file"]
            annotation_path = upload_dir / f"{base_name}.annotation"
            handle_upload(annotation_file, annotation_path)
            annotation_validation = annotation_validator(annotation_path)
            if annotation_validation["status"] != "valid":
                response = HttpResponseBadRequest()
                response.write(annotation_validation["message"])
                return response

        job = Job.objects.create(alias=alias,
                                 email=email,
                                 fasta_file=fasta_path,
                                 annotation_file=annotation_path)
        job.save()
        event = JobEvent.objects.create(job=job,
                                        date=creation_dt)
        event.save()
        email_body = EMAIL_TEMPLATES["experiment_created"]["body"].format(
            alias=alias,
            date=datetime.now().strftime("%d-%B-%Y"),
            token=job.token)
        subject = EMAIL_TEMPLATES["experiment_created"]["subject"]
        if email != "noemail@noemail.com":
            send_email(email, email_body, subject)
        return redirect(f"job/{job.token}")
    redirect("search")


def job_search(request):
    context = {"active": "job"}
    if request.method == "POST":
        log.info("yay mates")
        token = request.POST["token"]
        return redirect(f"job/{token}")
    return render(request, "base/job-search.html", context)


def get_job_or_json404(token):
    try:
        job = Job.objects.get(token=token)
        return True, job
    except Job.DoesNotExist:
        return False, JsonResponse({
                "error": "job not found"
            }, status=404)


@rw_protected_resource()
def ping(request):
    context = {}
    context["message"] = "pong"
    return JsonResponse(context)


@rw_protected_resource()
def pending_jobs(request):
    context = {}
    jobs = Job.objects.filter(status=Status.CREATED)
    context["jobs"] = [j.get_dict() for j in jobs]
    return JsonResponse(context)


@rw_protected_resource()
def job_details(request, token):
    success, job = get_job_or_json404(token)
    if not success:
        return job
    return JsonResponse(job.get_dict())


def download_job_file(path):
    context = {}
    if path:
        path = Path(path)
        if path.exists():
            response = StreamingHttpResponse(file_iterator(path))
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = ("attachment;filename="
                                               f"{path.name}")
            return response
    context = {"error": "file does not exist"}
    return JsonResponse(context, status=404)


@rw_protected_resource()
def job_fasta(request, token):
    success, job = get_job_or_json404(token)
    if not success:
        return job
    return download_job_file(job.fasta_file)


@rw_protected_resource()
def job_annot(request, token):
    success, job = get_job_or_json404(token)
    if not success:
        return job
    return download_job_file(job.annotation_file)


@csrf_exempt
@rw_protected_resource()
def job_update_result(request):
    context = {}
    status_code = 200
    if request.method == "POST":
        token = request.POST["token"]
        url = request.POST["url"]
        success, job = get_job_or_json404(token)
        if not success:
            return job
        job.result_file = url
        job.save()
        context["message"] = "successfully changed the result URL"
    if "message" not in context:
        context["message"] = "something went wrong!"
        status_code = 409
    return JsonResponse(context, status=status_code)


@csrf_exempt
@rw_protected_resource()
def job_update_status(request):
    context = {}
    status_code = 200
    if request.method == "POST":
        token = request.POST["token"]
        status = request.POST["status"]
        success, job = get_job_or_json404(token)
        if not success:
            return job
        current = job.status
        valid_transitions = [
            (Status.CREATED, Status.JOINED),
            (Status.JOINED, Status.STARTED),
            (Status.JOINED, Status.EXPIRED),
            (Status.STARTED, Status.FINISHED),
            (Status.STARTED, Status.FAILED),
            (Status.FINISHED, Status.EXPIRED),
        ]
        notify = False 
        for start, end in valid_transitions:
            if current == start and status == end:
                job.status = status
                job.save()
                event = JobEvent.objects.create(job=job,
                                                status=status,
                                                date=datetime.now())
                event.save()
                context["message"] = "successfully changed the status"
                if status == Status.STARTED:
                    notify = True
                    template = "experiment_started"
                elif status == Status.FINISHED:
                    notify = True
                    template = "experiment_finished"
                if notify:
                    date = datetime.now().strftime("%d-%B-%Y")
                    email_body = (EMAIL_TEMPLATES[template]["body"]
                                  .format(alias=job.alias,
                                          date=date,
                                          token=job.token))
                    subject = EMAIL_TEMPLATES[template]["subject"]
                    send_email(job.email, email_body, subject)
        if "message" not in context:
            context["message"] = f"can't change from {current} to {status}"
            status_code = 409
    return JsonResponse(context, status=status_code)


def job(request, token):
    context = {"active": "job"}
    job = get_object_or_404(Job, token=token)
    context["job"] = job
    return render(request, "base/job.html", context)


def results(request):
    context = {"active": "job"}
    return render(request, "base/home.html", context)


def about(request):
    context = {"active": "about"}
    return render(request, "base/about.html", context)
