import os
from unittest.mock import Mock

import pytest
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from sdx_base.run import run
from sdx_base.services.storage import StorageService
from sdx_base.services.http import HttpService
from sdx_base.services.pubsub import PubsubService
from sdx_base.server.server import RouterConfig
from sdx_base.server.tx_id import txid_from_pubsub

from app.dependencies import get_storage_service, get_pubsub_service, get_http_service
from app.settings import Settings
from app.routes import router


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


@pytest.fixture(scope="session")
def test_client():
    """
    General client for hitting endpoints in tests
    """
    os.environ["PROJECT_ID"] = "ons-sdx-sandbox"
    proj_root = Path(__file__).parent  # sdx-seft dir
    router_config = RouterConfig(
        router, tx_id_getter=txid_from_pubsub
    )
    app: FastAPI = run(
        Settings,
        routers=[router_config],
        proj_root=proj_root,
        serve=lambda a, b: a,
    )

    test_client = TestClient(app)
    return test_client
