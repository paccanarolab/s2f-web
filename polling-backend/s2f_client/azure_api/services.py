from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from pathlib import Path
from typing import Dict
from s2f_client.tools.services import query_yes_no
import os
import logging


logger = logging.getLogger(__name__)
CONNECT_STR = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_ACCOUNT = os.getenv("AZURE_ACCOUNT")
BASE_URL = f"https://{AZURE_ACCOUNT}.blob.core.windows.net"


def upload_result_file(job: Dict, result_file: Path):
    token = job["token"]
    logger.info("creaing container")
    blob_service_client = BlobServiceClient.from_connection_string(CONNECT_STR)
    try:
        container_client = blob_service_client.create_container(
            token, public_access="container")
    except ResourceExistsError:
        container_client = blob_service_client.get_container_client(token)
    blob_client = blob_service_client.get_blob_client(
        container=token,
        blob=result_file.name)
    # Upload the created file
    logger.info(f"uploading file {result_file}")
    with open(file=result_file, mode="rb") as data:
        blob_client.upload_blob(data)
    logger.info("listing container blobs")
    blob_list = container_client.list_blobs()
    for blob in blob_list:
        logger.info(f"\t{blob.name}")


def delete_job_container(job: str):
    token = job["token"]
    blob_service_client = BlobServiceClient.from_connection_string(CONNECT_STR)
    try:
        container_client = blob_service_client.get_container_client(
            container=token)
        container_client.delete_container()
    except ResourceNotFoundError:
        logger.info("the container was already deleted")


def delete_all_containers():
    blob_service_client = BlobServiceClient.from_connection_string(CONNECT_STR)

    for container in blob_service_client.list_containers():
        name = container["name"]
        print(f">>> container name = {name}")
        container_client = blob_service_client.get_container_client(name)
        if query_yes_no(f"delete container with name {name}?", default="no"):
            container_client.delete_container()
            logger.info(f"deleted {name}")


def list_all_containers():
    logger.info(CONNECT_STR)
    blob_service_client = BlobServiceClient.from_connection_string(CONNECT_STR)

    for container in blob_service_client.list_containers():
        name = container["name"]
        print(f">>> container name = {name}")
        container_client = blob_service_client.get_container_client(name)
        print("List of blobs...")
        # List the blobs in the container
        blob_list = container_client.list_blobs()
        for blob in blob_list:
            print(f"\t{blob.name}")
            print(f"\t{BASE_URL}/{name}/{blob.name}")
