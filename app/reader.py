from app import CONFIG
import structlog

logger = structlog.get_logger()


def read(filename) -> bytes:
    logger.info('Getting SEFT file as bytes')
    filepath = f"/{filename}"
    # get bucket data as blob
    blob = CONFIG.BUCKET.blob(filename)
    # convert to bytes
    data_bytes = blob.download_as_bytes()

    return data_bytes
