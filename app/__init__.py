import os
import structlog
from app.logger import logging_config
from google.cloud import pubsub_v1, storage
from flask import Flask
from app import routes

logging_config()
logger = structlog.get_logger()
project_id = os.getenv('PROJECT_ID', 'ons-sdx-lucas')


class Config:
    """class to hold required configuration data"""

    def __init__(self, proj_id) -> None:
        self.PROJECT_ID = proj_id
        self.BUCKET_NAME = f'{proj_id}-seft-responses'
        self.BUCKET = None
        self.SEFT_SUBSCRIPTION_ID = "seft-subscription"
        self.SEFT_SUBSCRIPTION_PATH = None
        self.SEFT_SUBSCRIBER = None
        self.QUARANTINE_SEFT_TOPIC_ID = "quarantine-seft-topic"
        self.QUARANTINE_TOPIC_PATH = None
        self.QUARANTINE_SEFT_PUBLISHER = None
        self.DELIVER_SERVICE_URL = os.getenv('DELIVER_SERVICE_URL', "http://sdx-deliver:80")


CONFIG = Config(project_id)


def cloud_config():
    """
    Loads configuration required for running against GCP based environments

    This function makes calls to GCP native tools such as Google PubSub
    and therefore should not be called in situations where these connections are
    not possible, e.g running the unit tests locally.
    """
    logger.info('Loading cloud config')

    storage_client = storage.Client(CONFIG.PROJECT_ID)
    CONFIG.BUCKET = storage_client.bucket(CONFIG.BUCKET_NAME)

    seft_subscriber = pubsub_v1.SubscriberClient()
    CONFIG.SEFT_SUBSCRIBER = seft_subscriber
    CONFIG.SEFT_SUBSCRIPTION_PATH = seft_subscriber.subscription_path(CONFIG.PROJECT_ID, CONFIG.SEFT_SUBSCRIPTION_ID)

    # publish config
    quarantine_seft_publisher = pubsub_v1.PublisherClient()
    CONFIG.QUARANTINE_TOPIC_PATH = quarantine_seft_publisher.topic_path(CONFIG.PROJECT_ID, CONFIG.QUARANTINE_SEFT_TOPIC_ID)
    CONFIG.QUARANTINE_SEFT_PUBLISHER = quarantine_seft_publisher


app = Flask(__name__)

