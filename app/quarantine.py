from app import CONFIG


def quarantine_submission(message, tx_id: str, error: str):
    data = message.data
    future = CONFIG.QUARANTINE_SEFT_PUBLISHER.publish(CONFIG.QUARANTINE_TOPIC_PATH, data, tx_id=tx_id, error=error)
    return future.result()
