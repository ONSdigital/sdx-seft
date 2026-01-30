import base64
import json
from typing import cast
from unittest.mock import Mock, MagicMock

import pytest

from sdx_base.errors.errors import DataError
from sdx_base.models.pubsub import Message

from app.definitions.definitions import SurveyType
from app.services.process_service import (
    ProcessService,
    SettingsProtocol,
    ReadProtocol, PubsubProtocol,
)
from app.services.deliver_service import DeliverService


def make_pubsub_message(payload: dict) -> Message:
    """
    Helpers to create a mock Pub/Sub message with base64 encoded data
    :param payload:
    :return:
    """
    message = MagicMock(spec=Message)

    encoded = base64.b64encode(
        json.dumps(payload).encode("utf-8")
    )

    message.__getitem__.side_effect = lambda key: encoded if key == "data" else None
    return cast(Message, message)


@pytest.fixture
def settings() -> SettingsProtocol:
    settings = Mock(spec=SettingsProtocol)
    settings.get_bucket_name.return_value = "test-bucket"
    settings.project_id = "test-project"
    settings.quarantine_topic_id = "test-quarantine-topic"
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


@pytest.fixture
def pubsub_service() -> PubsubProtocol:
    return cast(PubsubProtocol, Mock(spec=PubsubProtocol))


def test_process_message_reads_file_and_delivers_seft(
    settings: SettingsProtocol,
    storage_service: ReadProtocol,
    deliver_service: DeliverService,
    pubsub_service: PubsubProtocol,
):
    # Create ProcessService instance
    process_service = ProcessService(
        settings=settings,
        storage_service=storage_service,
        deliver_service=deliver_service,
        pubsub_service=pubsub_service,
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
    message = make_pubsub_message(meta_dict)

    # call the process_message method
    process_service.process_message(message)

    # Assert the storage protocol read method was called with correct parameters
    storage_service.read.assert_called_once_with(
        "test.seft",
        "test-bucket",
    )

    # Assert the deliver_seft method was called with correct parameters
    deliver_service.deliver.assert_called_once_with(
        SurveyType.SEFT,
        meta_dict,
        meta_dict["filename"],
        b"file-bytes",
    )


def test_process_message_raises_error_when_filename_missing(
    settings: SettingsProtocol,
    storage_service: ReadProtocol,
    deliver_service: DeliverService,
    pubsub_service: PubsubProtocol,
):
    # Arrange
    process_service = ProcessService(
        settings=settings,
        storage_service=storage_service,
        deliver_service=deliver_service,
        pubsub_service=pubsub_service
    )

    # Set up invalid metadata dictionary (missing filename)
    message = make_pubsub_message({"tx_id": "tx-123"})

    # Assert that DataError is raised
    with pytest.raises(DataError):
        process_service.process_message(message)

    # Ensure no calls were made to storage or deliver services
    storage_service.read.assert_not_called()
    deliver_service.deliver.assert_not_called()


def test_quarantine_message_calls_pubsub_correctly(
    settings: SettingsProtocol,
    storage_service: ReadProtocol,
    deliver_service: DeliverService,
    pubsub_service: PubsubProtocol,
):
    # Arrange
    process_service = ProcessService(
        settings=settings,
        storage_service=storage_service,
        deliver_service=deliver_service,
        pubsub_service=pubsub_service,
    )

    payload = {"tx_id": "tx-123"}
    reason = "test reason"
    message = make_pubsub_message(payload)

    # Act
    process_service.quarantine_message(message, reason)

    # Assert
    pubsub_service.quarantine_error.assert_called_once_with(
        f"projects/{settings.project_id}/topics/{settings.quarantine_topic_id}",
        DataError,
        reason,
        "tx-123",
    )
