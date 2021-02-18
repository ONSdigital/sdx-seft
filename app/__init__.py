import os
from app.logger import logging_config
from google.cloud import pubsub_v1, storage

logging_config()

PROJECT_ID = os.getenv('PROJECT_ID', 'ons-sdx-sandbox')
BUCKET_NAME = f'{PROJECT_ID}-sefts'

# create storage client
storage_client = storage.Client(PROJECT_ID)
# get bucket with name
BUCKET = storage_client.bucket(BUCKET_NAME)

# Subscriber config
subscription_id = "seft-subscription"
seft_subscriber = pubsub_v1.SubscriberClient()
subscription_path = seft_subscriber.subscription_path(PROJECT_ID, subscription_id)

# publish config
quarantine_seft_topic_id = "quarantine-seft-topic"
quarantine_seft_publisher = pubsub_v1.PublisherClient()
quarantine_topic_path = quarantine_seft_publisher.topic_path(PROJECT_ID, quarantine_seft_topic_id)

# deliver url
DELIVER_SERVICE_URL = "sdx-deliver:80"
