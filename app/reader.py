from google.cloud import storage
from app import BUCKET_NAME, PROJECT_ID


def read(filename) -> bytes:
    # create storage client
    storage_client = storage.Client(PROJECT_ID)
    # get bucket with name
    bucket = storage_client.bucket(BUCKET_NAME)
    # get bucket data as blob
    blob = bucket.blob(filename)
    # convert to bytes
    data_bytes = blob.download_as_bytes()

    return data_bytes
