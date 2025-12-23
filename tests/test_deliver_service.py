import json
from typing import cast
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
def settings() -> Mock[SettingsProtocol]:
    settings = Mock(spec=SettingsProtocol)
    settings.deliver_service_url = "https://sdx-deliver.test"
    return settings


@pytest.fixture
def http_service() -> Mock[HttpProtocol]:
    return Mock(spec=HttpProtocol)


def test_deliver_seft_posts_correct_payload(
        settings: SettingsProtocol,
        http_service: HttpProtocol):

    # Create a Deliver service instance
    service = DeliverService(settings=settings, http_service=http_service)

    # Set up a metadata dictionary
    meta_dict = Metadata(**{
        "filename": "test.seft",
        "tx_id": "tx-123",
        "survey_id": "001",
        "period": "202401",
        "ru_ref": "12345678901",
    })

    # Set up SEFT file bytes
    file_bytes = b"seft-file-content"

    expected_context = {
        "survey_id": "001",
        "period_id": "202401",
        "ru_ref": "12345678901",
        "tx_id": "tx-123",
        "survey_type": "seft",
        "context_type": "business_survey",
    }

    # Call the deliver_seft method
    service.deliver_seft(meta_dict, file_bytes)

    # Assert that the HTTP POST was called once
    http_service.post.assert_called_once()

    # Extract the arguments used in the HTTP POST call for verification
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
