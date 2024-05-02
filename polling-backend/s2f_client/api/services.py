from typing import Dict
from oauthlib.oauth2 import BackendApplicationClient, TokenExpiredError
from requests_oauthlib import OAuth2Session
from datetime import datetime
from pathlib import Path


API_URL = "https://localhost"
PADDING_SECONDS = 10
CLIENT_ID = "Nn5yWZQw5JLOF5RvXrzsOWgVieMo8VjEAin3nTzu"
CLIENT_SECRET = "Z58yafK76EOuZearQLmK7wpRTFQ6sJVIYIxhEtpdBSJb18WKZzSAf0aI66XMxAaQFa0u8SyMJpIVPnMZ99te41DkCDKrnnNqWDFfPymSIcrw1UgBYHLuKRifqDAFWORB"
TOKEN = {}
CLIENT = None


def _refresh_token():
    global CLIENT, TOKEN
    TOKEN = CLIENT.fetch_token(f"{API_URL}/o/token/",
                               client_id=CLIENT_ID,
                               client_secret=CLIENT_SECRET)
    c = BackendApplicationClient(client_id=CLIENT_ID)
    CLIENT = OAuth2Session(client=c, token=TOKEN)
    print("refreshed token")


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


def init_api():
    global CLIENT, TOKEN
    c = BackendApplicationClient(client_id=CLIENT_ID)
    CLIENT = OAuth2Session(client=c)
    TOKEN = CLIENT.fetch_token(token_url='https://localhost/o/token/',
                               client_id=CLIENT_ID,
                               client_secret=CLIENT_SECRET)
    CLIENT = OAuth2Session(client=c, token=TOKEN)


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
