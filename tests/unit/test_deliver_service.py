import json
from typing import cast
from unittest.mock import Mock

import pytest

from app.config.deliver_config import deliver_config
from app.definitions.definitions import Metadata, SurveyType
from app.services.deliver_service import (
    DeliverService,
    FILE_NAME,
    TX_ID,
    CONTEXT,
    SettingsProtocol,
    HttpProtocol,
)


@pytest.fixture
def settings() -> SettingsProtocol:
    settings = Mock(spec=SettingsProtocol)
    settings.deliver_service_url = "https://sdx-deliver.test"
    return cast(SettingsProtocol, settings)


@pytest.fixture
def http_service() -> HttpProtocol:
    return cast(HttpProtocol, Mock(spec=HttpProtocol))


def test_deliver_seft_posts_correct_payload(
        settings: SettingsProtocol,
        http_service: HttpProtocol):

    # Create a Deliver service instance
    service = DeliverService(settings=settings, http_service=http_service, deliver_config=deliver_config)

    ru_ref = "90826421137"
    ru_check = "T"
    period = "202112"
    tx_id = "20220920110706"
    survey_id = "266"
    filename = f"{ru_ref}{ru_check}_{period}_{survey_id}_{tx_id}.xlsx.gpg"

    # Set up a metadata dictionary
    meta_dict = Metadata(**{
        "filename": filename,
        "tx_id": tx_id,
        "survey_id": survey_id,
        "period": period,
        "ru_ref": ru_ref,
        "ru_check": ru_check,
    })

    # Set up SEFT file bytes
    file_bytes = b"seft-file-content"

    expected_context = {
        "survey_id": survey_id,
        "period_id": period,
        "ru_ref": ru_ref,
        "tx_id": tx_id,
        "survey_type": SurveyType.SEFT,
        "context_type": "business_survey",
    }

    # Call the deliver_seft method
    service.deliver(SurveyType.SEFT, meta_dict, meta_dict["filename"], file_bytes)

    # Assert that the HTTP POST was called once
    http_service.post.assert_called_once()

    # Extract the arguments used in the HTTP POST call for verification
    domain, endpoint = http_service.post.call_args.args
    kwargs = http_service.post.call_args.kwargs

    assert domain == settings.deliver_service_url
    assert endpoint == deliver_config[SurveyType.SEFT]["endpoint"]

    params = kwargs["params"]
    assert params[FILE_NAME] == filename
    assert params[TX_ID] == tx_id
    assert json.loads(params[CONTEXT]) == expected_context

    files = kwargs["files"]
    assert files[deliver_config[SurveyType.SEFT]["file_key"]] == file_bytes


def test_deliver_seft_receipt_posts_correct_payload(
    settings: SettingsProtocol,
    http_service: HttpProtocol):

    # Create a Deliver service instance
    service = DeliverService(settings=settings, http_service=http_service, deliver_config=deliver_config)

    ru_ref = "90826421137"
    ru_check = "T"
    period = "202112"
    tx_id = "20220920110706"
    survey_id = "266"
    filename = f"{ru_ref}{ru_check}_{period}_{survey_id}_{tx_id}.xlsx.gpg"
    zip_filename = tx_id

    # Set up a metadata dictionary
    meta_dict = Metadata(**{
        "filename": filename,
        "tx_id": tx_id,
        "survey_id": survey_id,
        "period": period,
        "ru_ref": ru_ref,
        "ru_check": ru_check,
    })

    # Set up SEFT receipt file bytes
    file_bytes = b"seft-receipt-zipped-bytes"

    expected_context = {
        "survey_id": survey_id,
        "period_id": period,
        "ru_ref": ru_ref,
        "tx_id": tx_id,
        "survey_type": SurveyType.SEFT_RECEIPT,
        "context_type": "business_survey",
    }

    # Call the deliver_seft method
    service.deliver(SurveyType.SEFT_RECEIPT, meta_dict, zip_filename, file_bytes)

    # Assert that the HTTP POST was called once
    http_service.post.assert_called_once()

    # Extract the arguments used in the HTTP POST call for verification
    domain, endpoint = http_service.post.call_args.args
    kwargs = http_service.post.call_args.kwargs

    assert domain == settings.deliver_service_url
    assert endpoint == deliver_config[SurveyType.SEFT_RECEIPT]["endpoint"]

    params = kwargs["params"]

    assert params[FILE_NAME] == zip_filename
    assert params[TX_ID] == tx_id
    assert json.loads(params[CONTEXT]) == expected_context

    files = kwargs["files"]
    assert files[deliver_config[SurveyType.SEFT_RECEIPT]["file_key"]] == file_bytes
