import json
from unittest.mock import Mock

import pytest

from app.definitions import Metadata
from app.services.deliver_service import (
    DeliverService,
    FILE_NAME,
    TX_ID,
    CONTEXT,
    SEFT_FILE_V2, SettingsProtocol, HttpProtocol,
)


@pytest.fixture
def settings():
    settings = Mock(spec=SettingsProtocol)
    settings.deliver_service_url = "https://sdx-deliver.test"
    return settings


@pytest.fixture
def http_service():
    return Mock(spec=HttpProtocol)


def test_deliver_seft_posts_correct_payload(settings, http_service):
    # Arrange
    service = DeliverService(settings=settings, http_service=http_service)

    meta_dict = Metadata(**{
        "filename": "test.seft",
        "tx_id": "tx-123",
        "survey_id": "001",
        "period": "202401",
        "ru_ref": "12345678901",
    })

    file_bytes = b"seft-file-content"

    expected_context = {
        "survey_id": "001",
        "period_id": "202401",
        "ru_ref": "12345678901",
        "tx_id": "tx-123",
        "survey_type": "seft",
        "context_type": "business_survey",
    }

    # Act
    service.deliver_seft(meta_dict, file_bytes)

    # Assert
    http_service.post.assert_called_once()

    domain, endpoint = http_service.post.call_args.args
    kwargs = http_service.post.call_args.kwargs

    assert domain == settings.deliver_service_url
    assert endpoint == "deliver/v2/seft"

    params = kwargs["params"]
    assert params[FILE_NAME] == "test.seft"
    assert params[TX_ID] == "tx-123"
    assert json.loads(params[CONTEXT]) == expected_context

    files = kwargs["files"]
    assert files[SEFT_FILE_V2] == file_bytes
