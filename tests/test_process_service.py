import json
from typing import cast
from unittest.mock import Mock

import pytest

from sdx_base.errors.errors import DataError
from sdx_base.models.pubsub import Message

from app.services.process_service import (
    ProcessService,
    SettingsProtocol,
    ReadProtocol,
)
from app.services.deliver_service import DeliverService


@pytest.fixture
def settings() -> SettingsProtocol:
    settings = Mock(spec=SettingsProtocol)
    settings.get_bucket_name.return_value = "test-bucket"
    return cast(SettingsProtocol, settings)


@pytest.fixture
def storage_service() -> ReadProtocol:
    storage = Mock(spec=ReadProtocol)
    storage.read.return_value = b"file-bytes"
    return cast(ReadProtocol, storage)


@pytest.fixture
def deliver_service() -> DeliverService:
    deliver = Mock(spec=DeliverService)
    return cast(DeliverService, deliver)


def test_process_message_reads_file_and_delivers_seft(
    settings: SettingsProtocol,
    storage_service: ReadProtocol,
    deliver_service: DeliverService,
):
    # Create ProcessService instance
    process_service = ProcessService(
        settings=settings,
        storage_service=storage_service,
        deliver_service=deliver_service,
    )

    # Set up a valid metadata dictionary
    meta_dict = {
        "filename": "test.seft",
        "tx_id": "tx-123",
        "survey_id": "001",
        "period": "202401",
        "ru_ref": "12345678901",
    }

    # Cast mock to Message type to stop pycharm complaining
    message = cast(Message, Mock(spec=Message))
    message.data = json.dumps(meta_dict).encode()

    # call the process_message method
    process_service.process_message(message)

    # Assert the storage protocol read method was called with correct parameters
    storage_service.read.assert_called_once_with(
        "test.seft",
        "test-bucket",
    )

    # Assert the deliver_seft method was called with correct parameters
    deliver_service.deliver_seft.assert_called_once_with(
        meta_dict,
        b"file-bytes",
    )


def test_process_message_raises_error_when_filename_missing(
    settings: SettingsProtocol,
    storage_service: ReadProtocol,
    deliver_service: DeliverService,
):
    # Arrange
    process_service = ProcessService(
        settings=settings,
        storage_service=storage_service,
        deliver_service=deliver_service,
    )

    # Cast mock to Message type to stop pycharm complaining
    message = cast(Message, Mock(spec=Message))

    # Set up invalid metadata dictionary (missing filename)
    message.data = json.dumps({"tx_id": "tx-123"}).encode()

    # Assert that DataError is raised
    with pytest.raises(DataError):
        process_service.process_message(message)

    # Ensure no calls were made to storage or deliver services
    storage_service.read.assert_not_called()
    deliver_service.deliver_seft.assert_not_called()
