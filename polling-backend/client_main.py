import time
from datetime import datetime
from pathlib import Path
from s2f_client.api import services as api
from s2f_client.jobs import services as job_manager


MEDIA_ROOT = Path(__file__).parent / "experiments"
JOBS = []


if __name__ == "__main__":
    api.init_api()
    JOBS = job_manager.load_job_metas(MEDIA_ROOT)
    print("loaded jobs", JOBS)

    while True:
        r = api.get_job_list()
        for job in r["jobs"]:
            if job["token"] not in JOBS:
                job_manager.create_job_directory(MEDIA_ROOT, job)
            api.joined_job(job)
            JOBS[job["token"]] = job
        print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M")}]-{r}')
        for job in JOBS:
            print(job)
        time.sleep(10)
