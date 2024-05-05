from s2f_client.api import services as api
from s2f_client.azure_api import services as az_api
from s2f_client.jobs import services as job_manager
from s2f_client.tools import log
from pathlib import Path
import logging

log.setup_logger("s2f_client")


def step_all_jobs(args):
    media_root = Path(args.media_root)
    JOBS = []
    log.setup_logger("s2f client")
    logger = logging.getLogger('s2f client')
    api.init_api()
    # job_manager.clear_all_jobs(MEDIA_ROOT)
    JOBS = job_manager.load_job_metas(media_root)
    logger.info(f"loaded jobs {list(JOBS.keys())}")

    r = api.get_job_list()
    logger.info(f"job list {r}")

    logger.info(f"found {len(r['jobs'])} new jobs")
    for job in r["jobs"]:
        logger.info(f"job is {job}")
        JOBS[job["token"]] = job

    for token, job in JOBS.items():
        logger.info(f"handling job {token}")
        job = api.get_job_details(job)
        job_manager.update_job_meta(media_root, job)
        JOBS[token] = job
        job_manager.handle_job(media_root, job)


def delete_all_containers(args):
    az_api.delete_all_containers()


def list_all_containers(args):
    az_api.list_all_containers()
