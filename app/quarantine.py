from app import quarantine_seft_publisher, quarantine_topic_path


def quarantine_submission(data_str: str, tx_id: str):
    data = data_str.encode("utf-8")
    future = quarantine_seft_publisher.publish(quarantine_topic_path, data, tx_id=tx_id)
    return future.result()
