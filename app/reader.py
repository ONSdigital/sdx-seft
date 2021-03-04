from app import CONFIG


def read(filename) -> bytes:

    # get bucket data as blob
    blob = CONFIG.BUCKET.blob(filename)
    # convert to bytes
    data_bytes = blob.download_as_bytes()

    return data_bytes
