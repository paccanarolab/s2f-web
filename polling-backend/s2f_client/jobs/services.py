from typing import Dict
from pathlib import Path
from s2f_client.api import services as api
from s2f_client.azure_api import services as azure
import s2f_client.core.settings as settings
import json
import logging
import shutil
import subprocess
import configparser


logger = logging.getLogger(__name__)
history_handler = logging.FileHandler(
    settings.MEDIA_ROOT / "events.log", mode="a")
logger.addHandler(history_handler)


def _get_fake_prediction() -> str:
    return """
protein	go_id	score
protein 1	go_id	score
protein 2	go_id	score
protein 3	go_id	score
protein 4	go_id	score
protein 5	go_id	score
"""


def make_s2f_run_config(job):
    template = """[configuration]
config_file = {s2f_conf}
alias = {alias}
obo = {obo}
fasta = {fasta}
"""
    directory = settings.MEDIA_ROOT / job["token"]
    obo_file = settings.MEDIA_ROOT / "data" / "go.obo"
    run_config = directory / "run.conf"
    with run_config.open("w") as rc:
        rc.write(template.format(s2f_conf=settings.S2F_CONFIG,
                                 alias=job["token"],
                                 obo=obo_file,
                                 fasta=directory / "input.fasta"))


def make_prediction(job) -> bool:
    directory = settings.MEDIA_ROOT / job["token"]
    run_config = directory / "run.conf"
    result_directory = directory / "results"
    result_directory.mkdir()
    prediction_file = result_directory / "prediction.tsv"
    sentinel_file = result_directory / "prediction_done.txt"

    # create s2f run configuration file
    logger.info(f"creating S2F configuration file for {job['token']}")
    make_s2f_run_config(job)
    # run s2f predict command
    logger.info(f"running S2F with {job['token']} file")
    cmd = f"python {settings.S2F_ENTRY} --run-config {run_config}"
    subprocess.run(cmd, shell=True)
    # retrieve results
    with prediction_file.open("w") as outf:
        outf.write(_get_fake_prediction())
    # write sentinel file
    with sentinel_file.open("w") as outf:
        outf.write("done")
    sentinel_data = sentinel_file.open().read()
    return sentinel_data == "done"


def upload_prediction(job) -> str | None:
    directory = settings.MEDIA_ROOT / job["token"]
    result_directory = directory / "results"
    prediction_file = result_directory / "prediction.tsv"
    sentinel_file = result_directory / "prediction_done.txt"
    assert sentinel_file.exists()
    sentinel_data = sentinel_file.open().read()
    if sentinel_data == "done":
        azure.upload_result_file(job, prediction_file)
        return f"{azure.BASE_URL}/{job['token']}/prediction.tsv"


def create_job_directory(job):
    directory = settings.MEDIA_ROOT / job["token"]
    directory.mkdir(exist_ok=True)
    metadata = directory / "info.json"
    with metadata.open("w") as meta:
        json.dump(job, meta)


def update_job_meta(job):
    metadata = settings.MEDIA_ROOT / job["token"] / "info.json"
    if not metadata.exists():
        create_job_directory(job)
    with metadata.open("w") as meta:
        json.dump(job, meta)


def load_job_metas() -> Dict:
    jobs = {}
    for job_dir in settings.MEDIA_ROOT.iterdir():
        meta_json = job_dir / "info.json"
        if meta_json.exists():
            with meta_json.open() as mj:
                job = json.load(mj)
                jobs[job["token"]] = job
    return jobs


def get_manager_status() -> str:
    status_file = settings.MEDIA_ROOT / "manager_status.txt"
    if not status_file.is_file():
        set_manager_status("IDLE")
    return status_file.open().read()


def set_manager_status(status: str):
    status_file = settings.MEDIA_ROOT / "manager_status.txt"
    with status_file.open("w") as f:
        f.write(status)


def clear_all_jobs(directory: Path):
    for job_dir in directory.iterdir():
        if job_dir.is_dir():
            shutil.rmtree(job_dir, ignore_errors=True)


def change_job_status(job, status) -> bool:
    curr_status = job["status"]
    valid_transitions = [
        ("cr", "jo"),
        ("jo", "st"),
        ("jo", "ex"),
        ("st", "fi"),
        ("st", "fa"),
        ("fi", "ex"),
    ]
    for start, end in valid_transitions:
        if curr_status == start and status == end:
            return api.update_job_status(job, status)
    return False


def handle_job(job) -> bool:
    status = job["status"]
    logger.info(f"status {status}")
    job_directory = settings.MEDIA_ROOT / job["token"]
    result = False
    if status == "cr":
        if not job_directory.exists():
            create_job_directory(job)
        downloaded_file = api.download_fasta_file(job, job_directory)
        if downloaded_file is not None:
            result = change_job_status(job, "jo")
        else:
            result = False
    elif status == "jo":
        change_job_status(job, "st")
        result = make_prediction(job)
    elif status == "st":
        uploaded = upload_prediction(job)
        if uploaded is not None:
            api.update_job_result(job, uploaded)
            result = change_job_status(job, "fi")
    elif status == "fi":
        azure.delete_job_container(job)
        result = change_job_status(job, "ex")
    logger.info(f"done with {job['token']}, result is {result}\n")
    return result
