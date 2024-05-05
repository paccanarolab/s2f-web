import os
from azure.storage.blob import BlobServiceClient
from pathlib import Path
from ..tools.services import query_yes_no
from ..tools import log
import logging


log.setup_logger(__name__)
logger = logging.getLogger(__name__)

try:
    print("Azure Blob Storage Python quickstart sample")

    # Retrieve the connection string for use with the application. The storage
    # connection string is stored in an environment variable on the machine
    # running the application called AZURE_STORAGE_CONNECTION_STRING. If the
    # environment variable is created after the application is launched in a
    # console or with Visual Studio, the shell or application needs to be
    # closed and reloaded to take the environment variable into account.
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    base_url = "https://paccanarolabs2f.blob.core.windows.net"

    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    for container in blob_service_client.list_containers():
        name = container["name"]
        print(f">>> container name = {name}")
        container_client = blob_service_client.get_container_client(name)
        if query_yes_no(f"delete container with name {name}?", default="no"):
            container_client.delete_container()

except Exception as ex:
    print('Exception:')
    print(ex)
