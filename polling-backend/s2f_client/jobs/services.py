from typing import Dict
from pathlib import Path
from s2f_client.api import services as api
import json


def _get_fake_prediction() -> str:
    return """
protein	go_id	score
protein 1	go_id	score
protein 2	go_id	score
protein 3	go_id	score
protein 4	go_id	score
protein 5	go_id	score
"""


def make_prediction(media_root: Path, job):
    directory = media_root / job["token"]
    result_directory = directory / "results"
    result_directory.mkdir()
    prediction_file = result_directory / "prediction.tsv"
    with prediction_file.open("w") as outf:
        outf.write(_get_fake_prediction())


def create_job_directory(media_root: Path, job):
    directory = media_root / job["token"]
    directory.mkdir(exist_ok=True)
    metadata = directory / "info.json"
    with metadata.open("w") as meta:
        json.dump(job, meta)
    api.download_fasta_file(job, directory)


def load_job_metas(directory: Path) -> Dict:
    jobs = {}
    for job_dir in directory.iterdir():
        meta_json = job_dir / "info.json"
        if meta_json.exists():
            with meta_json.open() as mj:
                job = json.load(mj)
                jobs[job["token"]] = job
    return jobs
