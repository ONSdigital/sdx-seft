from app import CONFIG


def read(filename) -> bytes:

    filepath = f"/{filename}"
    # get bucket data as blob
    blob = CONFIG.BUCKET.blob(filepath)
    # convert to bytes
    data_bytes = blob.download_as_bytes()

    return data_bytes
