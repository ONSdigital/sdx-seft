import json
import structlog

from app.deliver import deliver_seft
from app.reader import read


logger = structlog.get_logger()


def process(message_str: str):
    """
    Retrieves the filename from the encrypted message and begins deliver_seft process
    """

    logger.info("Processing message")
    meta_dict = json.loads(message_str)
    filename = meta_dict.get("filename")
    data_bytes = read(filename)
    deliver_seft(meta_dict, data_bytes)


