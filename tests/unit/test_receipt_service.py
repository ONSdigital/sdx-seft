from typing import cast
from unittest.mock import Mock, patch

import pytest

from app.definitions.definitions import SurveyType
from app.services.deliver_service import DeliverService
from app.services.receipt_service import ReceiptService


@pytest.fixture
def deliver_service() -> DeliverService:
    deliver = Mock(spec=DeliverService)
    return cast(DeliverService, deliver)


@patch("app.services.receipt_service.create_zip")
def test_process_receipt(
    mock_create_zip: Mock,
    deliver_service: DeliverService,
):
    mock_create_zip.return_value = b'zipped-bytes'

    # Arrange
    receipt_service = ReceiptService(
        deliver_service=deliver_service,
    )

    meta_dict = {
        "survey_id": "123",
        "ru_ref": "90123456789",
        "ru_check": "T",
        "period": "202401",
        "tx_id": "123456",
    }

    # Act
    receipt_service.process_receipt(meta_dict)

    # Assert
    deliver_service.deliver.assert_called_once_with(
        SurveyType.SEFT_RECEIPT,
        meta_dict,
        "123456",
        b'zipped-bytes',
    )

def test_process_receipt_no_receipt_needed(
    deliver_service: DeliverService,
):
    # Arrange
    receipt_service = ReceiptService(
        deliver_service=deliver_service,
    )

    meta_dict = {
        "survey_id": "141", # Survey ID that does not require a receipt
        "ru_ref": "90123456789",
        "ru_check": "T",
        "period": "202401",
        "tx_id": "123456",
    }

    # Act
    receipt_service.process_receipt(meta_dict)

    # Assert
    deliver_service.deliver.assert_not_called()


def test_receipt_service_formulate_idbr_receipt(
    deliver_service: DeliverService,
):
    # Arrange
    receipt_service = ReceiptService(
        deliver_service=deliver_service,
    )

    survey_id = "123"
    ru_ref = "90123456789"
    ru_check = "T"
    period = "202401"

    # Act
    receipt_content = receipt_service._format_idbr_receipt(
        survey_id,
        ru_ref,
        ru_check,
        period
    )

    # Assert
    expected_receipt_content = f"{ru_ref}:{ru_check}:{survey_id}:{period}"

    assert receipt_content == expected_receipt_content


@patch("app.services.receipt_service.get_current_datetime_in_dm")
def test_receipt_service_formulate_idbr_receipt_name(
    mock_datetime: Mock,
    deliver_service: DeliverService,
):
    # Arrange
    receipt_service = ReceiptService(
        deliver_service=deliver_service,
    )

    mock_datetime.return_value = "0204"

    tx_id = "123456"

    # Act
    receipt_filename = receipt_service._formulate_idbr_receipt_name(tx_id)

    # Assert
    assert receipt_filename == f"REC0204_{tx_id}.DAT"
