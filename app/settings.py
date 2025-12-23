
from sdx_base.settings.app import AppSettings, get_settings


class Settings(AppSettings):
    quarantine_topic_id: str = "quarantine-seft-topic"
    deliver_service_url: str = "sdx-deliver:80"

    def get_bucket_name(self) -> str:
        return f'{self.project_id}-seft-responses'


def get_instance() -> Settings:
    return get_settings(Settings)
