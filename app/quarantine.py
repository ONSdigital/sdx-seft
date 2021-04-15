from app import CONFIG


def quarantine_submission(message: object, tx_id: str, error: str):
    """Publish the submission represented by message with tx_id and error as attributes to the seft quarantine topic."""
    data = message.data
    if tx_id is None:
        tx_id = 'No tx_id provided'
    future = CONFIG.QUARANTINE_SEFT_PUBLISHER.publish(CONFIG.QUARANTINE_TOPIC_PATH, data, tx_id=tx_id, error=error)
    return future.result()
