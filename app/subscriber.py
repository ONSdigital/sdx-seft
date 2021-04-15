import structlog
import threading
from concurrent.futures import TimeoutError

from structlog.contextvars import bind_contextvars, clear_contextvars
from app import CONFIG
from app.collect import process
from app.errors import RetryableError
from app.quarantine import quarantine_submission

logger = structlog.get_logger()


def callback(message):
    """
    Manages the life cycle of the received message.
    Handles pre processing events such as setting up logging bindings.
    Extracts the data and passes it on to be processed.
    Handles post processing events such acking the message and
    catching exceptions raised during processing.
    """
    tx_id = message.attributes.get('tx_id')
    bind_contextvars(app="SDX-SEFT")
    bind_contextvars(tx_id=tx_id)
    bind_contextvars(thread=threading.currentThread().getName())
    try:
        encrypted_message_str = message.data.decode('utf-8')
        process(encrypted_message_str)
        message.ack()
    except RetryableError as err:
        logger.error(f"Connection error: {str(err)}")
        message.nack()
    except Exception as e:
        logger.error(f"Quarantining message: error {str(e)}")
        quarantine_submission(message, tx_id, str(e))
        message.ack()
    finally:
        clear_contextvars()


def start():
    """
    Begin listening to the seft pubsub subscription.

    This functions spawns new threads that listen to the subscription topic and
    on receipt of a message invoke the callback function.

    The main thread blocks indefinitely unless the connection times out
    """
    streaming_pull_future = CONFIG.SEFT_SUBSCRIBER.subscribe(CONFIG.SEFT_SUBSCRIPTION_PATH, callback=callback)
    logger.info(f"Listening for messages on {CONFIG.SEFT_SUBSCRIPTION_PATH}..")

    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with CONFIG.SEFT_SUBSCRIBER:
        try:
            # Result() will block indefinitely, unless an exception is encountered first.
            streaming_pull_future.result()
        except TimeoutError:
            streaming_pull_future.cancel()
