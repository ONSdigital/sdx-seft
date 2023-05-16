import os

from sdx_gcp.app import get_logger, SdxApp

logger = get_logger()
project_id = os.getenv('PROJECT_ID', 'ons-sdx-sandbox')
deliver_service_url = os.getenv('DELIVER_SERVICE_URL', "sdx-deliver:80")


class Config:
    """class to hold required configuration data"""

    def __init__(self, proj_id) -> None:
        self.PROJECT_ID = proj_id
        self.BUCKET_NAME = f'{proj_id}-seft-responses'
        self.QUARANTINE_TOPIC_ID = "quarantine-seft-topic"
        self.DELIVER_SERVICE_URL = deliver_service_url


CONFIG = Config(project_id)

sdx_app = SdxApp("sdx-seft", project_id)
