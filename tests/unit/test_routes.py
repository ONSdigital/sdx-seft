import base64
import json
from unittest.mock import patch

from sdx_base.models.pubsub import Message, Envelope


@patch("app.services.process_service.get_data")
def test_testing(mock_get_data, test_client):
    payload = {
        "tx_id": "20220920110706",
        "filename": "90123456789T_202112_001_20220920110706.xlsx.gpg"
    }
    encrypted_payload = base64.b64encode(
        json.dumps(payload).encode("utf-8")
    )

    mock_get_data.return_value = json.dumps(payload)

    message: Message = {
        "attributes": {"objectId": "20220920110706"},
        "data": encrypted_payload.decode("utf-8"),
        "message_id": "test-id",
        "publish_time": "2022-09-20T11:07:06.000Z",
    }

    envelope: Envelope = {"message": message, "subscription": "test-subscription"}

    response = test_client.post(
        "/",
        json=envelope
    )

    assert response.status_code == 204
