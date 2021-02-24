import os
from app.logger import logging_config
from google.cloud import pubsub_v1, storage

logging_config()

project_id = os.getenv('PROJECT_ID', 'ons-sdx-sandbox')
DELIVER_SERVICE_URL = "sdx-deliver:80"


class Config:

    def __init__(self, proj_id) -> None:
        self.PROJECT_ID = proj_id
        self.BUCKET_NAME = f'{proj_id}-sefts'
        self.BUCKET = None
        self.SEFT_SUBSCRIPTION_ID = "seft-subscription"
        self.SEFT_SUBSCRIPTION_PATH = None
        self.SEFT_SUBSCRIBER = None
        self.QUARANTINE_SEFT_TOPIC_ID = "quarantine-seft-topic"
        self.QUARANTINE_TOPIC_PATH = None
        self.QUARANTINE_SEFT_PUBLISHER = None


CONFIG = Config(project_id)


def cloud_config():
    print('Loading cloud config')

    storage_client = storage.Client(CONFIG.PROJECT_ID)
    CONFIG.BUCKET = storage_client.bucket(CONFIG.BUCKET_NAME)

    seft_subscriber = pubsub_v1.SubscriberClient()
    CONFIG.SEFT_SUBSCRIBER = seft_subscriber
    CONFIG.SEFT_SUBSCRIPTION_PATH = seft_subscriber.subscription_path(CONFIG.PROJECT_ID, CONFIG.SEFT_SUBSCRIPTION_ID)

    # publish config
    quarantine_seft_publisher = pubsub_v1.PublisherClient()
    CONFIG.QUARANTINE_SEFT_PUBLISHER = quarantine_seft_publisher.topic_path(CONFIG.PROJECT_ID, CONFIG.QUARANTINE_SEFT_TOPIC_ID)
    CONFIG.QUARANTINE_SEFT_PUBLISHER = quarantine_seft_publisher
