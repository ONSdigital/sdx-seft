import base64
import json
import unittest
from unittest.mock import patch, Mock

from sdx_gcp import Message, Envelope
from sdx_gcp.app import SdxApp

from app.collect import process, get_tx_id
from app.deliver import FILE_NAME, METADATA_FILE, SEFT_FILE, TX_ID


def convert_data(data: dict) -> str:
    return base64.b64encode(json.dumps(data).encode()).decode("utf-8").strip()


class TestApp(unittest.TestCase):

    def setUp(self) -> None:

        self.data = {
            'filename': 'test.seft',
            'tx_id': '123',
            'survey_id': '057',
            'period': '202009',
            'ru_ref': '20210121143526',
            'md5sum': '12345',
            'sizeBytes': 42
        }

        self.message: Message = {
            "attributes": {},
            "data": "",
            "message_id": "123",
            "publish_time": "today"
        }

    @patch('app.collect.sdx_app')
    @patch('app.deliver.sdx_app.http_post')
    @patch('app.deliver.CONFIG')
    @patch('app.deliver.use_v2_endpoint')
    def test_process(self, mock_use_v2: Mock, mock_config: Mock, mock_post: Mock, mock_app: Mock):
        mock_use_v2.return_value = False
        tx_id = '123'
        file_bytes = b'seft_file_content'
        meta_bytes = json.dumps(self.data).encode()
        deliver_url = "sdx-deliver-url"

        self.message['data'] = convert_data(self.data)
        mock_config.DELIVER_SERVICE_URL = deliver_url
        mock_app.gcs_read.return_value = file_bytes

        process(self.message, tx_id)

        mock_post.assert_called_with(
            deliver_url,
            "deliver/seft",
            None,
            params={FILE_NAME: 'test.seft', TX_ID: tx_id},
            files={
                METADATA_FILE: meta_bytes,
                SEFT_FILE: file_bytes
            }
        )

    @patch('app.collect.deliver_seft')
    @patch('app.collect.sdx_app')
    @patch('app.deliver.use_v2_endpoint')
    def test_success_returns_204(self, mock_use_v2: Mock, mock_app: Mock, mock_deliver: Mock):
        mock_use_v2.return_value = False
        mock_app.gcs_read.return_value = b'seft_file_content'
        self.message['data'] = convert_data(self.data)
        envelope: Envelope = {
            'message': self.message,
            'subscription': 'seft_subscription'
        }

        sdx_app = SdxApp("sdx-seft", "ons-sdx-sandbox")
        sdx_app.add_pubsub_endpoint(process, "quarantine_topic", tx_id_getter=get_tx_id)

        with sdx_app.app.test_client() as c:
            resp = c.post("/", json=envelope)
            self.assertEqual(204, resp.status_code)

    @patch('app.collect.deliver_seft')
    @patch('app.collect.sdx_app')
    @patch('sdx_gcp.handlers.quarantine_error')
    @patch('app.deliver.use_v2_endpoint')
    def test_missing_filename_gets_quarantined(self, mock_use_v2: Mock, mock_quarantine: Mock, mock_app: Mock, mock_deliver: Mock):
        mock_use_v2.return_value = False
        mock_app.gcs_read.return_value = b'seft_file_content'
        del self.data['filename']
        self.message['data'] = convert_data(self.data)
        envelope: Envelope = {
            'message': self.message,
            'subscription': 'seft_subscription'
        }

        sdx_app = SdxApp("sdx-seft", "ons-sdx-sandbox")
        sdx_app.add_pubsub_endpoint(process, "quarantine_topic", tx_id_getter=get_tx_id)

        with sdx_app.app.test_client() as c:
            resp = c.post("/", json=envelope)
            self.assertEqual(204, resp.status_code)
            mock_quarantine.assert_called()
