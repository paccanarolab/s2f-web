from typing import Dict
from pathlib import Path
from s2f_client.api import services as api
from s2f_client.azure_api import services as azure
import json
import logging
import shutil

logger = logging.getLogger(__name__)


def _get_fake_prediction() -> str:
    return """
protein	go_id	score
protein 1	go_id	score
protein 2	go_id	score
protein 3	go_id	score
protein 4	go_id	score
protein 5	go_id	score
"""


def make_prediction(media_root: Path, job) -> bool:
    directory = media_root / job["token"]
    result_directory = directory / "results"
    result_directory.mkdir()
    prediction_file = result_directory / "prediction.tsv"
    sentinel_file = result_directory / "prediction_done.txt"
    with prediction_file.open("w") as outf:
        outf.write(_get_fake_prediction())
    with sentinel_file.open("w") as outf:
        outf.write("done")
    sentinel_data = sentinel_file.open().read()
    return sentinel_data == "done"


def upload_prediction(media_root: Path, job) -> str | None:
    directory = media_root / job["token"]
    result_directory = directory / "results"
    prediction_file = result_directory / "prediction.tsv"
    sentinel_file = result_directory / "prediction_done.txt"
    assert sentinel_file.exists()
    sentinel_data = sentinel_file.open().read()
    if sentinel_data == "done":
        azure.upload_result_file(job, prediction_file)
        return f"{azure.BASE_URL}/{job['token']}/prediction.tsv"


def create_job_directory(media_root: Path, job):
    directory = media_root / job["token"]
    directory.mkdir(exist_ok=True)
    metadata = directory / "info.json"
    with metadata.open("w") as meta:
        json.dump(job, meta)


def update_job_meta(media_root: Path, job):
    metadata = media_root / job["token"] / "info.json"
    if not metadata.exists():
        create_job_directory(media_root, job)
    with metadata.open("w") as meta:
        json.dump(job, meta)


def load_job_metas(directory: Path) -> Dict:
    jobs = {}
    for job_dir in directory.iterdir():
        meta_json = job_dir / "info.json"
        if meta_json.exists():
            with meta_json.open() as mj:
                job = json.load(mj)
                jobs[job["token"]] = job
    return jobs


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


def handle_job(media_root: Path, job) -> bool:
    status = job["status"]
    logger.info(f"status {status}")
    job_directory = media_root / job["token"]
    result = False
    if status == "cr":
        if not job_directory.exists():
            create_job_directory(media_root, job)
        downloaded_file = api.download_fasta_file(job, job_directory)
        if downloaded_file is not None:
            result = change_job_status(job, "jo")
        else:
            result = False
    elif status == "jo":
        change_job_status(job, "st")
        result = make_prediction(media_root, job)
    elif status == "st":
        uploaded = upload_prediction(media_root, job)
        if uploaded is not None:
            api.update_job_result(job, uploaded)
            result = change_job_status(job, "fi")
    elif status == "fi":
        azure.delete_job_container(job)
        result = change_job_status(job, "ex")
    logger.info(f"done with {job['token']}, result is {result}\n")
    return result
