import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class Status(models.TextChoices):
    CREATED = "cr", _("Experiment created")
    JOINED = "jo", _("Experiment joined the queue")
    STARTED = "st", _("Experiment started running")
    FINISHED = "fi", _("Experiment finished successfully")
    EXPIRED = "ex", _("Experiment files expired and deleted")
    FAILED = "fa", _("Experiment did not finish successfully")


class Job(models.Model):
    alias = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    status = models.TextField(max_length=2,
                              choices=Status,
                              default=Status.CREATED)
    fasta_file = models.TextField()
    annotation_file = models.TextField()
    result_file = models.TextField()


class JobEvent(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    status = models.TextField(max_length=2,
                              choices=Status,
                              default=Status.CREATED)
    date = models.DateTimeField()
