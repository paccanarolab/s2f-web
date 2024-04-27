from typing import Dict, List
from oauthlib.oauth2 import BackendApplicationClient, TokenExpiredError
from requests_oauthlib import OAuth2Session
import time
import json
from datetime import datetime
from pathlib import Path


API_URL = "https://localhost"
MEDIA_ROOT = Path(__file__).parent / "experiments"
CLIENT_ID = "Nn5yWZQw5JLOF5RvXrzsOWgVieMo8VjEAin3nTzu"
CLIENT_SECRET = "Z58yafK76EOuZearQLmK7wpRTFQ6sJVIYIxhEtpdBSJb18WKZzSAf0aI66XMxAaQFa0u8SyMJpIVPnMZ99te41DkCDKrnnNqWDFfPymSIcrw1UgBYHLuKRifqDAFWORB"
TOKEN = {}
CLIENT = None
PADDING_SECONDS = 10
JOBS = []


def _refresh_token():
    global CLIENT, TOKEN
    TOKEN = CLIENT.fetch_token(f"{API_URL}/o/token/",
                               client_id=CLIENT_ID,
                               client_secret=CLIENT_SECRET)
    client = BackendApplicationClient(client_id=CLIENT_ID)
    CLIENT = OAuth2Session(client=client, token=TOKEN)
    print("refreshed token")
    print(TOKEN)


def _ensure_authenticated():
    try:
        delta = TOKEN["expires_at"] - datetime.now().timestamp()
        print(f"{delta=}")
        if delta < PADDING_SECONDS:
            _refresh_token()
        r = CLIENT.get(f"{API_URL}/api/ping")
        d = r.json()
    except TokenExpiredError:
        print("except")
        _refresh_token()
        r = CLIENT.get(f"{API_URL}/api/ping")
        d = r.json()
    return d["message"] == "pong"


def get_job_list() -> Dict:
    _ensure_authenticated()
    r = CLIENT.get(f"{API_URL}/api/pending_jobs")
    return r.json()


def get_job_files(job) -> Dict:
    _ensure_authenticated()
    r = CLIENT.get(f'{API_URL}/api/job_files/{job["token"]}')
    return r.json()


def download_fasta_file(job, fasta_dir) -> Path | None:
    _ensure_authenticated()
    url = f'{API_URL}/api/job_fasta/{job["token"]}'
    with CLIENT.get(url, stream=True) as r:
        if r.status_code == 200:
            filename = r.headers["Content-Disposition"].split("=")[1]
            fasta_path = fasta_dir / filename
            with fasta_path.open("wb") as fasta:
                for chunk in r.iter_content(512):
                    fasta.write(chunk)
            return fasta_path
        else:
            return None


def joined_job(job):
    _ensure_authenticated()
    r = CLIENT.post(f"{API_URL}/api/update_job_status",
                    data={
                        "token": job["token"],
                        "status": "jo"
                        })
    print(r.text)


def create_job_directory(job):
    directory = MEDIA_ROOT / job["token"]
    directory.mkdir(exist_ok=True)
    metadata = directory / "info.json"
    with metadata.open("w") as meta:
        json.dump(job, meta)
    download_fasta_file(job, directory)


def load_job_metas(directory: Path) -> List:
    jobs = []
    for job_dir in directory.iterdir():
        meta_json = job_dir / "meta.json"
        if meta_json.exists():
            with meta_json.open() as mj:
                jobs.append(json.load(mj))
    return jobs


if __name__ == "__main__":
    client = BackendApplicationClient(client_id=CLIENT_ID)
    oauth = OAuth2Session(client=client)
    TOKEN = oauth.fetch_token(token_url='https://localhost/o/token/',
                              client_id=CLIENT_ID,
                              client_secret=CLIENT_SECRET)
    print(TOKEN)
    print(datetime.now().timestamp())
    CLIENT = OAuth2Session(client=client, token=TOKEN)
    r = CLIENT.get("https://localhost/api/pending_jobs")
    JOBS = load_job_metas(MEDIA_ROOT)

    while True:
        r = get_job_list()
        for job in r["jobs"]:
            JOBS.append(job)
            create_job_directory(job)
            joined_job(job)
        print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M")}]-{r}')
        for job in JOBS:
            print(job)
        time.sleep(10)
