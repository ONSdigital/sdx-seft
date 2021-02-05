from google.cloud import storage
from app import BUCKET_NAME, PROJECT_ID


def read(filename) -> bytes:

    filepath = f"/{filename}"
    # create storage client
    storage_client = storage.Client(PROJECT_ID)
    # get bucket with name
    bucket = storage_client.bucket(BUCKET_NAME)
    # get bucket data as blob
    blob = bucket.blob(filepath)
    # convert to bytes
    data_bytes = blob.download_as_bytes()

    return data_bytes
