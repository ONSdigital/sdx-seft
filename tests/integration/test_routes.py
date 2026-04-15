import base64
import datetime
import json

from sdx_base.errors.errors import DataError
from sdx_base.models.pubsub import Message, Envelope
from starlette.testclient import TestClient

from app.config.deliver_config import deliver_config
from app.definitions.definitions import SurveyType, Context
from app.functions.zip_function import create_zip
from app.services.deliver_service import FILE_NAME, CONTEXT, TX_ID
from tests.test_data.integration_test_data import TestDataContainer

from tests.test_data.mock_settings import MOCK_BUCKET_NAME, MOCK_DELIVER_SERVICE_URL

MOCK_RECEIPT_DATE = datetime.datetime(2023, 4, 20, 12, 0, 0, 0)


def test_seft_and_receipt_deliver_success(test_client: TestClient, storage_mock, http_mock):
    """
    Test the successful delivery of both SEFT file and receipt when receipt is required.

    Test procedures:
    1. Setup test data with valid metadata and survey ID that requires a receipt.
    2. Call the endpoint with the test data envelope.
    3. Assert that the response status code is 204.
    4. Assert that the SEFT file was read from storage with the correct filename and bucket.
    5. Assert that the SEFT file was delivered to sdx-deliver with the correct parameters and file bytes.
    6. Assert that the SEFT receipt was delivered to sdx-deliver with the correct parameters and receipt bytes.
    """

    # TODO, this test needs refectoring

    # ------------------------
    # Setup test data
    # ------------------------

    timestamp = "20220920110706"
    ru_ref = "90123456789"
    ru_check = "T"
    period = "202112"
    survey_id = "001"

    tx_id = f"{ru_ref}{ru_check}_{period}_{survey_id}_{timestamp}"
    file_name = f"{tx_id}.xlsx.gpg"
    data = base64.b64encode(
        "hello, world".encode("utf-8")
    ).decode("utf-8")

    # ------------------------
    # Setup Envelope
    # ------------------------

    message: Message = {
        "attributes": {
            "objectId": file_name,
        },
        "data": data,
        "message_id": "test-id",
        "publish_time": MOCK_RECEIPT_DATE.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    }

    envelope: Envelope = {"message": message, "subscription": "test-subscription"}

    # ------------------------
    # Call the endpoint
    # ------------------------

    # Call endpoint with test data envelope
    response = test_client.post(
        "/",
        json=envelope
    )

    # ------------------------
    # Assertions
    # ------------------------

    # Assert status code
    assert response.status_code == 204

    # Assert SEFT file read from storage
    storage_mock.read.assert_called_once_with(
        file_name,
        MOCK_BUCKET_NAME,
    )

    expected_context: Context = {
            "survey_id": survey_id,
            "period_id": period,
            "ru_ref": ru_ref,
            "tx_id": tx_id,
            "survey_type": SurveyType.SEFT,
            "context_type": "business_survey"
    }

    # Assert deliver was called with correct parameters for SEFT file
    http_mock.post.assert_any_call(
        MOCK_DELIVER_SERVICE_URL,
        deliver_config[SurveyType.SEFT]['endpoint'],
        params={
            FILE_NAME: file_name,
            TX_ID: tx_id,
            CONTEXT: json.dumps(expected_context),
        },
        files={
            deliver_config[SurveyType.SEFT]['file_key']: storage_mock.read.return_value
        }
    )

    receipt_context: Context = {
        "survey_id": survey_id,
        "period_id": period,
        "ru_ref": ru_ref,
        "tx_id": tx_id,
        "survey_type": SurveyType.SEFT_RECEIPT,
        "context_type": "business_survey"
    }

    receipt_filename = f"REC{MOCK_RECEIPT_DATE.strftime("%d%m")}_{tx_id}.DAT"
    receipt_bytes = bytes(f"{ru_ref}:{ru_check}:{survey_id}:{period}", "utf-8")
    receipt_zip_bytes = create_zip({receipt_filename: receipt_bytes})

    # Assert SEFT receipt delivery
    http_mock.post.assert_called_with(
        MOCK_DELIVER_SERVICE_URL,
        deliver_config[SurveyType.SEFT_RECEIPT]['endpoint'],
        params={
            FILE_NAME: f"{tx_id}_receipt.zip",
            TX_ID: tx_id,
            CONTEXT: json.dumps(receipt_context),
        },
        files={
            deliver_config[SurveyType.SEFT_RECEIPT]['file_key']: receipt_zip_bytes
        }
    )


def test_seft_deliver_success_when_receipt_not_required(test_client: TestClient, storage_mock, http_mock):
    """
    Test the successful delivery of SEFT file when receipt is not required.

    Test procedures:
    1. Setup test data with valid metadata and survey ID that does not require a receipt.
    2. Call the endpoint with the test data envelope.
    3. Assert that the response status code is 204.
    4. Assert that the SEFT file was read from storage with the correct filename and bucket.
    5. Assert that the HTTP Post was called only once with the correct parameters and file bytes of SEFT.
    """

    # TODO, this test needs refectoring

    # ------------------------
    # Setup test data
    # ------------------------

    timestamp = "20220920110706"
    ru_ref = "90123456789"
    ru_check = "T"
    period = "202112"
    survey_id = "141"  # Survey ID that does not require a receipt

    tx_id = f"{ru_ref}{ru_check}_{period}_{survey_id}_{timestamp}"
    file_name = f"{tx_id}.xlsx.gpg"
    data = base64.b64encode(
        "hello, world".encode("utf-8")
    ).decode("utf-8")

    # ------------------------
    # Setup Envelope
    # ------------------------

    message: Message = {
        "attributes": {
            "objectId": file_name,
        },
        "data": data,
        "message_id": "test-id",
        "publish_time": MOCK_RECEIPT_DATE.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    }

    envelope: Envelope = {"message": message, "subscription": "test-subscription"}

    response = test_client.post(
        "/",
        json=envelope
    )

    assert response.status_code == 204

    # Ensure the seft was read from storage
    storage_mock.read.assert_called_once_with(
        file_name,
        MOCK_BUCKET_NAME,
    )

    expected_context: Context = {
        "survey_id": survey_id,
        "period_id": period,
        "ru_ref": ru_ref,
        "tx_id": tx_id,
        "survey_type": SurveyType.SEFT,
        "context_type": "business_survey"
    }

    # Assert the http service was only called ONCE (no receipt sent)
    http_mock.post.assert_called_once_with(
        MOCK_DELIVER_SERVICE_URL,
        deliver_config[SurveyType.SEFT]['endpoint'],
        params={
            FILE_NAME: file_name,
            TX_ID: tx_id,
            CONTEXT: json.dumps(expected_context),
        },
        files={
            deliver_config[SurveyType.SEFT]['file_key']: storage_mock.read.return_value
        }
    )


def test_send_quarantine_message_when_metadata_incomplete(test_client: TestClient, storage_mock, http_mock, pubsub_mock):
    """
    Test that a quarantine message is sent when the metadata is incomplete and cannot be processed.

    Test procedures:
    1. Setup test data with an invalid `ru_ref` to trigger metadata processing failure.
    2. Call the endpoint with the test data envelope.
    3. Assert that the response status code is 400
    4. Assert that the SEFT file read from storage was not called.
    5. Assert that the HTTP Post was not called.
    """

    # TODO this was changed from a 204 to a 400, previously it would quarantine
    # if ru_ref or something was incorrect, but now everything comes from metadata (filename)
    # so there will be no guarantee of a tx_id being extracted

    # ------------------------
    # Setup test data
    # ------------------------

    timestamp = "20220920110706"
    ru_check = "T"
    period = "202112"
    survey_id = "001"
    ru_ref = "1234"  # Invalid ru_ref to trigger metadata processing failure

    tx_id = f"{ru_ref}{ru_check}_{period}_{survey_id}_{timestamp}"
    file_name = f"{tx_id}.xlsx.gpg"
    data = base64.b64encode(
        "hello, world".encode("utf-8")
    ).decode("utf-8")

    # ------------------------
    # Setup Envelope
    # ------------------------

    message: Message = {
        "attributes": {
            "objectId": file_name,
        },
        "data": data,
        "message_id": "test-id",
        "publish_time": MOCK_RECEIPT_DATE.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    }

    envelope: Envelope = {"message": message, "subscription": "test-subscription"}

    # ------------------------
    # Call the endpoint
    # ------------------------

    response = test_client.post(
        "/",
        json=envelope
    )

    # ------------------------
    # Assertions
    # ------------------------

    assert response.status_code == 400  # TODO see comment at top

    # Assert we did not attempt to read the seft
    storage_mock.read.assert_not_called()

    # Assert we did not attempt to deliver seft
    http_mock.post.assert_not_called()


def test_send_quarantine_message_when_seft_file_read_fails(test_client, storage_mock, http_mock, pubsub_mock):
    """
    Test that a quarantine message is sent when reading the SEFT file from storage fails.

    Test procedures:
    1. Setup test data with valid metadata.
    2. Mock the storage read method to raise a DataError to simulate a failure in reading the SEFT file.
    3. Call the endpoint with the test data envelope.
    4. Assert that the response status code is 204.
    5. Assert that the SEFT file read from storage was called once with the correct filename and bucket.
    6. Assert that the HTTP Post was not called.
    7. Assert that a quarantine message was sent to Pub/Sub.
    """

    # ------------------------
    # Setup test data
    # ------------------------

    timestamp = "20220920110706"
    ru_ref = "90123456789"
    ru_check = "T"
    period = "202112"
    survey_id = "001"

    tx_id = f"{ru_ref}{ru_check}_{period}_{survey_id}_{timestamp}"
    file_name = f"{tx_id}.xlsx.gpg"
    data = base64.b64encode(
        "hello, world".encode("utf-8")
    ).decode("utf-8")

    # ------------------------
    # Setup Envelope
    # ------------------------

    message: Message = {
        "attributes": {
            "objectId": file_name,
        },
        "data": data,
        "message_id": "test-id",
        "publish_time": MOCK_RECEIPT_DATE.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    }

    envelope: Envelope = {"message": message, "subscription": "test-subscription"}

    # ------------------------
    # Side effects
    # ------------------------

    storage_mock.read.side_effect = DataError("Failed to read SEFT file")

    # ------------------------
    # Call endpoint
    # ------------------------

    response = test_client.post(
        "/",
        json=envelope
    )

    # ------------------------
    # Assertions
    # ------------------------

    assert response.status_code == 204

    # Assert that we attempted to read the seft file
    storage_mock.read.assert_called_once_with(
        file_name,
        MOCK_BUCKET_NAME,
    )

    # Assert we never got far enough to call deliver
    http_mock.post.assert_not_called()

    # Assert the file was quarantined
    pubsub_mock.quarantine_error.assert_called_once()
