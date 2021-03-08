import json
import structlog

from app.deliver import deliver_seft
from app.quarantine import quarantine_submission
from app.reader import read


logger = structlog.get_logger()


def process(message_str: str):

    logger.info("processing message", message_string=message_str)
    # logger.info(message_str)
    meta_dict = json.loads(message_str)
    tx_id = meta_dict.get("tx_id")
    filename = meta_dict.get("filename")

    try:
        data_bytes = read(filename)
        deliver_seft(meta_dict, data_bytes)

    except Exception as e:
        logger.info("quarantining message")
        logger.exception(e)
        quarantine_submission(message_str, tx_id)


