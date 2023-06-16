import json
from sdx_gcp import Message, get_data, Request, get_message, TX_ID
from sdx_gcp.app import get_logger
from sdx_gcp.errors import DataError

from app import sdx_app, CONFIG
from app.deliver import deliver_seft


logger = get_logger()


def process(message: Message, tx_id: TX_ID):
    """
    Retrieves the filename from the encrypted message and begins deliver_seft process
    """
    data: str = get_data(message)
    logger.info(f"Seft triggered by PubSub message with data: {data}")

    meta_dict = json.loads(data)
    if "filename" not in meta_dict:
        raise DataError("Missing filename from data!")
    filename = meta_dict.get("filename")
    data_bytes = sdx_app.gcs_read(filename, CONFIG.BUCKET_NAME)
    deliver_seft(meta_dict, data_bytes)

    logger.info("Process completed successfully")


def get_tx_id(req: Request) -> str:
    logger.info(f"Extracting tx_id from {req}")
    message: Message = get_message(req)
    tx_id = message["attributes"].get("tx_id")
    if not tx_id:
        data = get_data(message)
        meta_dict = json.loads(data)
        tx_id = meta_dict.get("tx_id")
    return tx_id
