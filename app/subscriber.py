import structlog
import threading
from concurrent.futures import TimeoutError

from structlog.contextvars import bind_contextvars, clear_contextvars
from app import seft_subscriber, subscription_path
from app.collect import process
from app.errors import RetryableError

logger = structlog.get_logger()


def callback(message):
    try:
        tx_id = message.attributes.get('tx_id')
        bind_contextvars(app="SDX-SEFT")
        bind_contextvars(tx_id=tx_id)
        bind_contextvars(thread=threading.currentThread().getName())
        encrypted_message_str = message.data.decode('utf-8')
        process(encrypted_message_str)
        message.ack()
    except RetryableError:
        logger.info("retryable error, nacking message")
        message.nack()
    except Exception as e:
        logger.error(f"error {str(e)}, nacking message")
        message.nack()
    finally:
        clear_contextvars()


def start():

    streaming_pull_future = seft_subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}..\n")

    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with seft_subscriber:
        try:
            # Result() will block indefinitely, unless an exception is encountered first.
            streaming_pull_future.result()
        except TimeoutError:
            streaming_pull_future.cancel()
