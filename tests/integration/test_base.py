import base64
import json
import os
import unittest
from pathlib import Path
from unittest.mock import Mock

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sdx_base.models.pubsub import Message, Envelope
from sdx_base.run import run
from sdx_base.server.server import RouterConfig
from sdx_base.server.tx_id import txid_from_pubsub
from sdx_base.services.http import HttpService
from sdx_base.services.pubsub import PubsubService
from sdx_base.services.storage import StorageService

from app.dependencies import get_storage_service, get_pubsub_service, get_http_service
from app.routes import router
from app.settings import Settings


class TestFdi(unittest.TestCase):

    def test_fdi(self):
        os.environ["PROJECT_ID"] = "ons-sdx-sandbox"
        proj_root = Path(__file__).parent.parent.parent  # sdx-seft dir

        router_config = RouterConfig(router, tx_id_getter=txid_from_pubsub)
        app: FastAPI = run(
            Settings,
            routers=[router_config],
            proj_root=proj_root,
            serve=lambda a, b: a,
        )

        mock_storage = Mock(spec=StorageService)
        mock_storage.read.return_value = b"seft bytes"
        app.dependency_overrides[get_storage_service] = lambda: mock_storage

        mock_http = Mock(spec=HttpService)
        app.dependency_overrides[get_http_service] = lambda: mock_http

        mock_pubsub = Mock(spec=PubsubService)
        app.dependency_overrides[get_pubsub_service] = lambda: mock_pubsub

        client = TestClient(app)

        filename = "60226421137T_202112_062_20220920110706.xlsx"

        data: str = base64.b64encode(json.dumps({"filename": filename}).encode()).decode()

        message: Message = {
            "attributes": {"objectId": "to be set in test"},
            "data": data,
            "message_id": "",
            "publish_time": "",
        }

        envelope: Envelope = {"message": message, "subscription": ""}

        resp = client.post("/", json=envelope)

        self.assertTrue(resp.is_success)
