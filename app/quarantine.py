from app import CONFIG


def quarantine_submission(data_str: str, tx_id: str):
    data = data_str.encode("utf-8")
    future = CONFIG.QUARANTINE_SEFT_PUBLISHER.publish(CONFIG.QUARANTINE_TOPIC_PATH, data, tx_id=tx_id)
    return future.result()
