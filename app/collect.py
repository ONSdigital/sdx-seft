import json
import logging

from structlog import wrap_logger

from app.deliver import deliver_seft
from app.quarantine import quarantine_submission
from app.reader import read

logger = wrap_logger(logging.getLogger(__name__))


def process(encrypted_message_str: str):

    logger.info("processing message")
    meta_dict = json.loads(encrypted_message_str)
    tx_id = meta_dict.get("tx_id")
    filename = meta_dict.get("filename")

    try:
        data_bytes = read(filename)
        deliver_seft(meta_dict, data_bytes)

    except Exception as e:
        logger.info("quarantining message")
        logger.error(str(e))
        quarantine_submission(encrypted_message_str, tx_id)


