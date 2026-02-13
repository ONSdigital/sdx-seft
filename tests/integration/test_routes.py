import json

from sdx_base.errors.errors import DataError

from app.config.deliver_config import deliver_config
from app.definitions.definitions import SurveyType
from app.services.deliver_service import FILE_NAME, CONTEXT, TX_ID
from tests.test_data.integration_test_data import TestDataContainer

from tests.test_data.mock_settings import MOCK_BUCKET_NAME, MOCK_DELIVER_SERVICE_URL


def test_seft_and_receipt_deliver_success(test_client, storage_mock, http_mock):
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
    tx_id = "20220920110706"
    ru_ref = "90123456789"
    ru_check = "T"
    period = "202112"
    survey_id = "001"

    # Setup test data
    test_data = TestDataContainer(tx_id, ru_ref, ru_check, period, survey_id)

    # Call endpoint with test data envelope
    response = test_client.post(
        "/",
        json=test_data.envelope
    )

    # Assert status code
    assert response.status_code == 204

    # Assert SEFT file read from storage
    storage_mock.read.assert_called_once_with(
        test_data.seft_filename,
        MOCK_BUCKET_NAME,
    )

    # Assert SEFT file delivery
    http_mock.post.assert_any_call(
        MOCK_DELIVER_SERVICE_URL,
        deliver_config[SurveyType.SEFT]['endpoint'],
        params={
            FILE_NAME: test_data.seft_filename,
            TX_ID: tx_id,
            CONTEXT: json.dumps(test_data.seft_context),
        },
        files={
            deliver_config[SurveyType.SEFT]['file_key']: storage_mock.read.return_value
        }
    )

    # Assert SEFT receipt delivery
    http_mock.post.assert_called_with(
        MOCK_DELIVER_SERVICE_URL,
        deliver_config[SurveyType.SEFT_RECEIPT]['endpoint'],
        params={
            FILE_NAME: tx_id,
            TX_ID: tx_id,
            CONTEXT: json.dumps(test_data.receipt_context),
        },
        files={
            deliver_config[SurveyType.SEFT_RECEIPT]['file_key']: test_data.receipt_zip_bytes
        }
    )


def test_seft_deliver_success_when_receipt_not_required(test_client, storage_mock, http_mock):
    """
    Test the successful delivery of SEFT file when receipt is not required.

    Test procedures:
    1. Setup test data with valid metadata and survey ID that does not require a receipt.
    2. Call the endpoint with the test data envelope.
    3. Assert that the response status code is 204.
    4. Assert that the SEFT file was read from storage with the correct filename and bucket.
    5. Assert that the HTTP Post was called only once with the correct parameters and file bytes of SEFT.
    """
    tx_id = "20220920110706"
    ru_ref = "90123456789"
    ru_check = "T"
    period = "202112"

    # Survey ID that does not require a receipt
    survey_id = "141"

    test_data = TestDataContainer(tx_id, ru_ref, ru_check, period, survey_id)

    response = test_client.post(
        "/",
        json=test_data.envelope
    )

    assert response.status_code == 204
    storage_mock.read.assert_called_once_with(
        test_data.seft_filename,
        MOCK_BUCKET_NAME,
    )

    http_mock.post.assert_called_once_with(
        MOCK_DELIVER_SERVICE_URL,
        deliver_config[SurveyType.SEFT]['endpoint'],
        params={
            FILE_NAME: test_data.seft_filename,
            TX_ID: tx_id,
            CONTEXT: json.dumps(test_data.seft_context),
        },
        files={
            deliver_config[SurveyType.SEFT]['file_key']: storage_mock.read.return_value
        }
    )


def test_send_quarantine_message_when_metadata_incomplete(test_client, storage_mock, http_mock, pubsub_mock):
    """
    Test that a quarantine message is sent when the metadata is incomplete and cannot be processed.

    Test procedures:
    1. Setup test data with an invalid `ru_ref` to trigger metadata processing failure.
    2. Call the endpoint with the test data envelope.
    3. Assert that the response status code is 204.
    4. Assert that the SEFT file read from storage was not called.
    5. Assert that the HTTP Post was not called.
    6. Assert that a quarantine message was sent to Pub/Sub.
    """
    tx_id = "20220920110706"
    ru_check = "T"
    period = "202112"
    survey_id = "001"

    # Invalid ru_ref to trigger metadata processing failure
    ru_ref = "1234"

    test_data = TestDataContainer(tx_id, ru_ref, ru_check, period, survey_id)

    response = test_client.post(
        "/",
        json=test_data.envelope
    )

    assert response.status_code == 204
    storage_mock.read.assert_not_called()
    http_mock.post.assert_not_called()

    pubsub_mock.quarantine_error.assert_called_once()


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
    tx_id = "20220920110706"
    ru_ref = "90123456789"
    ru_check = "T"
    period = "202112"
    survey_id = "001"

    test_data = TestDataContainer(tx_id, ru_ref, ru_check, period, survey_id)

    storage_mock.read.side_effect = DataError("Failed to read SEFT file")

    response = test_client.post(
        "/",
        json=test_data.envelope
    )

    assert response.status_code == 204
    storage_mock.read.assert_called_once_with(
        test_data.seft_filename,
        MOCK_BUCKET_NAME,
    )
    http_mock.post.assert_not_called()

    pubsub_mock.quarantine_error.assert_called_once()
