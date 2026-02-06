import os

import pytest
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sdx_base.run import run
from sdx_base.server.server import RouterConfig
from sdx_base.server.tx_id import txid_from_pubsub

from app.settings import Settings
from app.routes import router


@pytest.fixture
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
    yield test_client
