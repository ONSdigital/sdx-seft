import unittest
from unittest.mock import patch, Mock

from app import cloud_config, project_id
from app.logger import _MaxLevelFilter


class TestInit(unittest.TestCase):

    @patch('app.storage.Client')
    @patch('app.pubsub_v1')
    def test_cloud_config(self, mock_pubsub, mock_storage_client):
        mock_pubsub.SubscriberClient.return_value = Mock()
        cloud_config()
        mock_storage_client.assert_called_with(project_id)

    def test_logger(self):
        ml = _MaxLevelFilter(4)
        mock_log_record = Mock()
        mock_log_record.levelno = 3
        self.assertTrue(ml.filter(mock_log_record))
