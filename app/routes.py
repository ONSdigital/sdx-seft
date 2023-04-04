import structlog
from flask import request
from structlog.contextvars import bind_contextvars, clear_contextvars

from app import app
from app.collect import process
from app.errors import RetryableError
from app.quarantine import quarantine_submission

logger = structlog.get_logger()


@app.route("/", methods=["POST"])
def index():
    """Only expect to recieve messages pushed from pub/sub"""
    try:
        envelope = request.get_json()
        pubsub_message = envelope["message"]
        attributes = pubsub_message["attributes"]
        tx_id = attributes['objectId']
        bind_contextvars(app="SDX-Seft")
        bind_contextvars(tx_id=tx_id)

    except Exception as e:
        logger.error("Message in the wrong format!", error=str(e))
        # return 204 to ensure the message is 'acked'
        return f"Bad Request: {str(e)}", 204

    try:
        process(tx_id)
        return "", 204

    except RetryableError as r:
        logger.error("Retryable error, nacking message", error=str(r))
        # return 500 to ensure the message is 'nacked'
        return f"Retryable error", 500

    except Exception as error:
        logger.error(f"Quarantining message due to error: {str(error)}")
        quarantine_submission(tx_id, str(error))
        # return 204 to ensure the message is 'acked'
        return f"Bad Request: {str(error)}", 204

    finally:
        clear_contextvars()
