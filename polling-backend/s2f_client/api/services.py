from typing import Dict
from oauthlib.oauth2 import BackendApplicationClient, TokenExpiredError
from requests_oauthlib import OAuth2Session
from datetime import datetime
from pathlib import Path
import logging
import os


logger = logging.getLogger(__name__)
API_URL = os.getenv("S2F_API_URL", "https://localhost")
print(API_URL)
PADDING_SECONDS = 10
CLIENT_ID = os.getenv("S2F_CLIENT_ID")
CLIENT_SECRET = os.getenv("S2F_CLIENT_SECRET")
TOKEN = {}
CLIENT = None


def _refresh_token():
    global CLIENT, TOKEN
    TOKEN = CLIENT.fetch_token(f"{API_URL}/o/token/",
                               client_id=CLIENT_ID,
                               client_secret=CLIENT_SECRET)
    c = BackendApplicationClient(client_id=CLIENT_ID)
    CLIENT = OAuth2Session(client=c, token=TOKEN)
    logger.info("refreshed token")


def _ensure_authenticated():
    try:
        delta = TOKEN["expires_at"] - datetime.now().timestamp()
        if delta < PADDING_SECONDS:
            _refresh_token()
        r = CLIENT.get(f"{API_URL}/api/ping")
        d = r.json()
    except TokenExpiredError:
        logger.info("Token expired")
        _refresh_token()
        r = CLIENT.get(f"{API_URL}/api/ping")
        d = r.json()
    return d["message"] == "pong"


def init_api():
    global CLIENT, TOKEN
    c = BackendApplicationClient(client_id=CLIENT_ID)
    CLIENT = OAuth2Session(client=c)
    TOKEN = CLIENT.fetch_token(token_url=f"{API_URL}/o/token/",
                               client_id=CLIENT_ID,
                               client_secret=CLIENT_SECRET)
    CLIENT = OAuth2Session(client=c, token=TOKEN)


def get_job_list() -> Dict:
    _ensure_authenticated()
    r = CLIENT.get(f"{API_URL}/api/pending_jobs")
    return r.json()


def get_job_details(job) -> Dict:
    _ensure_authenticated()
    r = CLIENT.get(f'{API_URL}/api/job_details/{job["token"]}')
    return r.json()


def download_fasta_file(job, fasta_dir) -> Path | None:
    _ensure_authenticated()
    url = f'{API_URL}/api/job_fasta/{job["token"]}'
    with CLIENT.get(url, stream=True) as r:
        if r.status_code == 200:
            # filename = r.headers["Content-Disposition"].split("=")[1]
            filename = "input.fasta"
            fasta_path = fasta_dir / filename
            with fasta_path.open("wb") as fasta:
                for chunk in r.iter_content(512):
                    fasta.write(chunk)
            return fasta_path
        else:
            return None


def update_job_status(job, status):
    _ensure_authenticated()
    r = CLIENT.post(f"{API_URL}/api/update_job_status",
                    data={
                        "token": job["token"],
                        "status": status
                        })
    if r.status_code != 200:
        logger.error(r.text)
    return r.status_code == 200


def update_job_result(job, url):
    _ensure_authenticated()
    r = CLIENT.post(f"{API_URL}/api/update_job_result",
                    data={
                        "token": job["token"],
                        "url": url
                        })
    return r.status_code == 200
