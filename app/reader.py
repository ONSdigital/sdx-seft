from app import CONFIG
import structlog

logger = structlog.get_logger()


def read(filename) -> bytes:
    """
    Retrieve a seft from seft input bucket
    """
    logger.info('Getting SEFT file as bytes')
    blob = CONFIG.BUCKET.blob(filename)
    data_bytes = blob.download_as_bytes()

    return data_bytes
