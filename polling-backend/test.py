from typing import Dict, List, Optional

from oauthlib.oauth2 import BackendApplicationClient, TokenExpiredError
from requests_oauthlib import OAuth2Session
import json
import time
from datetime import datetime


API_URL = "https://localhost"
CLIENT_ID = "yrBWkPCeWYIF25cAAO8VwaG69e8HqHmsofs9kGVy"
CLIENT_SECRET = "0ifUtWfQtKWPliatxw2JsWbdpfSkUGKNCmJDrxJCBQQfzOx7Jr4Aymd4KDLiC31rTWCdg2LtlK720yMZUOW6XdvFihrvriNeyDd7dpQsUHx6GSePk9k3x1U9a7kzty17"
TOKEN = {}
CLIENT = None
PADDING_SECONDS = 10


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


def joined_job(job):
    _ensure_authenticated()
    r = CLIENT.post(f"{API_URL}/api/update_job_status",
                    data={
                        "token": job["token"],
                        "status": "jo"
                        })
    print(r.text)


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

    while True:
        r = get_job_list()
        for job in r["jobs"]:
            joined_job(job)
        print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M")}]-{r}')
        time.sleep(1)
