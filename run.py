from sdx_gcp.app import get_logger

from app import sdx_app, CONFIG
from app.collect import process, get_tx_id

logger = get_logger()


if __name__ == '__main__':
    sdx_app.add_pubsub_endpoint(process, CONFIG.QUARANTINE_TOPIC_ID, tx_id_getter=get_tx_id)
    sdx_app.run(port=5000)
