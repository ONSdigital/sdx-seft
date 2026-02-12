from sdx_base.settings.app import AppSettings, get_settings

MOCK_BUCKET_NAME = 'mock-bucket-name'
MOCK_DELIVER_SERVICE_URL = "mock-deliver-url"


class MockSettings(AppSettings):
    quarantine_topic_id: str = "mock-quarantine-seft-topic"
    deliver_service_url: str = MOCK_DELIVER_SERVICE_URL

    def get_bucket_name(self) -> str:
        return MOCK_BUCKET_NAME


def mock_get_instance() -> MockSettings:
    return get_settings(MockSettings)
