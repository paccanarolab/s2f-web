import os, uuid
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from pathlib import Path

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

    # Create a unique name for the container
    container_name = "test-container-name"

    # Create the container
    # container_client = blob_service_client.create_container(container_name)

    for container in blob_service_client.list_containers():
        name = container["name"]
        print(f">>> container name = {name}")
        container_client = blob_service_client.get_container_client(name)
        print("\nListing blobs...")

        # List the blobs in the container
        blob_list = container_client.list_blobs()
        for blob in blob_list:
            print("\t" + blob.name)
            print(f"\t{base_url}/{name}/{blob.name}")

    # Create a local directory to hold blob data
    local_path = Path("./data")
    local_path.mkdir(exist_ok=True)

    # Create a file in the local data directory to upload and download
    local_file_name = str(uuid.uuid4()) + ".txt"
    local_file_name = "prediction.tsv"
    upload_file_path = local_path / local_file_name
    upload_file_path = local_path / "prediction.tsv"

    # Write text to the file
    # file = open(file=upload_file_path, mode='w')
    # file.write("Hello, World!")
    # file.close()

    # Create a blob client using the local file name as the name for the blob
    # blob_client = blob_service_client.get_blob_client(
    #         #container="s2f",
    #         container=container_name,
    #         blob=local_file_name)

    # print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)

    # # Upload the created file
    # with open(file=upload_file_path, mode="rb") as data:
    #     blob_client.upload_blob(data)

    # print("\nListing blobs...")

    # container_client = blob_service_client.get_container_client(container_name)
    # # List the blobs in the container
    # blob_list = container_client.list_blobs()
    # for blob in blob_list:
    #     print("\t" + blob.name)
    #     print(f"\t{base_url}/{container_name}/{blob.name}")
    # # List the blobs in the container
    # blob_list = container_client.list_blobs()
    # for blob in blob_list:
    #     print("\t" + blob.name)

except Exception as ex:
    print('Exception:')
    print(ex)
