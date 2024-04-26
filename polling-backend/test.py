from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

import requests
import random
import string
import json


API_URL = "http://localhost"
CLIENT_ID = "U6ablNxNDpOaDtrMoqI4wfsvuYU2sfPQY0VyYT5u"
CLIENT_SECRET = "kOHLA1aODgRWa6QSGpDfftv9IleVLpOXRTTzSlmTBYF0G8evN9R0ChR7YV9LuP5t2T6hu2gUYrwhXcwugfObSYfJf6RPBCGF0UNVUKP9jUkoOsCrc6O7RYNio1g1H8nz"
TOKEN = ""


def _open_request(endpoint: str,
                  data: Optional[Dict] = None,
                  headers: Optional[Dict] = None,
                  method: str = "GET") -> requests.Response:
    url = f"{API_URL}/{endpoint}"
    if not headers:
        headers = {"accept": "application/json"}
    return requests.request(
        method,
        url,
        headers=headers,
        data=data,
    )


def _refresh_api_token() -> str:
    global TOKEN
    print(f"current access token: {TOKEN}\nRefreshing...")
    data = {
        "grant_type": "refresh_token",
        "scope": "read write",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    token_data = _open_request(
        "o/token/",
        data=data,
        method="POST"
    ).json()
    TOKEN = token_data["access_token"]
    print(f"current access token: {TOKEN}")
    return TOKEN


def _ensure_authenticated() -> None:
    url = f"{API_URL}/o/token"
    headers = {}
    headers["Authorization"] = f"Bearer {TOKEN}"
    response = requests.request(
        "GET",
        url,
        headers=headers,
    )
    print(response)
    _refresh_api_token()
    if response.status_code == 401:
        _refresh_api_token()


def _authenticated_request(endpoint: str,
                           data: Optional[Dict] = None,
                           headers: Optional[Dict] = None,
                           files: Optional[Dict] = None,
                           method: str = "POST") -> requests.Response:
    _ensure_authenticated()
    url = f"{API_URL}/{endpoint}"
    if not headers:
        headers = {}
    if "Authorization" not in headers:
        headers["Authorization"] = f"Bearer {TOKEN}"
    response = requests.request(
        method,
        url,
        headers=headers,
        data=data,
        files=files
    )
    return response


def get_job_list():
    print(_authenticated_request("api/pending_jobs", method="GET"))


def get_experiment(token: str) -> Dict:
    return _open_request(f"experiment/{token}").json()


def get_experiment_history(token: str) -> Dict:
    history = _open_request(f"experiment/events/{token}").json()
    for event in history:
        event["date_event"] = datetime.fromisoformat(event["date_event"])
    return history


def get_experiment_proteins(token: str) -> List:
    return _open_request(f"experiment/proteins/{token}").json()


def get_experiment_results(token: str, protein: str) -> List:
    data = {"protein": protein}
    return _open_request(
        f"experiment/results/{token}",
        data=data
    ).json()


def submit_experiment(data: Dict, files: Dict) -> Dict:
    print(files)
    return _authenticated_request(
        "experiment/",
        data=data,
        files=files
    ).json()


def get_fake_proteins(n: int) -> List:
    proteins = []
    vocab = string.ascii_uppercase + string.digits
    prot_len = 7
    for _ in range(n):
        proteins.append("".join(
            random.choice(vocab) for _ in range(prot_len)
        ))
    return proteins


if __name__ == "__main__":
    get_job_list()
