import os
from unittest.mock import Mock

import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from sdx_base.run import run
from sdx_base.server.tx_id import txid_not_applicable
from sdx_base.services.storage import StorageService
from sdx_base.services.http import HttpService
from sdx_base.services.pubsub import PubsubService
from sdx_base.server.server import RouterConfig
from sdx_base.run import initialise

from app.dependencies import get_storage_service, get_pubsub_service, get_http_service, get_settings, \
    get_datetime_service
from app.routes import router
from app.services.datetime_service import DatetimeService
from app.settings import ROOT
from tests.test_data.integration_test_data import MOCK_RECEIPT_DATE
from tests.test_data.mock_settings import MockSettings, mock_get_instance


@pytest.fixture(autouse=True)
def datetime_mock(test_client):
    app = test_client.app
    mock_datetime = Mock(spec=DatetimeService)
    mock_datetime.get_current_datetime_in_dm.return_value = MOCK_RECEIPT_DATE.strftime("%d%m")
    app.dependency_overrides[get_datetime_service] = lambda: mock_datetime

    yield mock_datetime


@pytest.fixture(autouse=True)
def storage_mock(test_client):
    """
    """
    app = test_client.app
    mock_storage = Mock(spec=StorageService)
    mock_storage.read.return_value = b"seft bytes"
    app.dependency_overrides[get_storage_service] = lambda: mock_storage

    yield mock_storage


@pytest.fixture(autouse=True)
def http_mock(test_client):
    """
    """
    app = test_client.app
    mock_http = Mock(spec=HttpService)
    app.dependency_overrides[get_http_service] = lambda: mock_http

    yield mock_http


@pytest.fixture(autouse=True)
def pubsub_mock(test_client):
    """
    """
    app = test_client.app
    mock_pubsub = Mock(spec=PubsubService)
    app.dependency_overrides[get_pubsub_service] = lambda: mock_pubsub

    yield mock_pubsub


@pytest.fixture(autouse=True)
def settings_mock(test_client):
    """
    """
    app = test_client.app
    app.dependency_overrides[get_settings] = mock_get_instance


@pytest.fixture
def test_app() -> FastAPI:
    """
    This fixture will create a FastAPI app using SDX base
    """

    # Set environment variable for testing
    os.environ["PROJECT_ID"] = "ons-sdx-sandbox"

    class MockSecretReader:
        def get_secret(self, project_id: str, secret_id: str) -> str:
            return "secret"

    return initialise(
        settings=MockSettings,
        routers=[RouterConfig(router, tx_id_getter=txid_not_applicable)],
        proj_root=ROOT,
        secret_reader=MockSecretReader,
    )


@pytest.fixture
def test_client(test_app: FastAPI) -> TestClient:
    """
    General client for hitting endpoints in tests
    """

    test_client = TestClient(test_app)
    return test_client
