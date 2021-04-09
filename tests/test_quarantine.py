import unittest
from unittest.mock import patch, Mock

from app.quarantine import quarantine_submission


class TestInit(unittest.TestCase):

    @patch('app.quarantine.CONFIG')
    def test_quarantine_submission(self, mock_config):
        mock_message = Mock()
        mock_message.data = "silly message"
        mock_config.QUARANTINE_TOPIC_PATH = "quarantine_path"
        tx_id = "123"
        error = "bad error"
        quarantine_submission(mock_message, tx_id, error)
        mock_config.QUARANTINE_SEFT_PUBLISHER.publish.assert_called_with(
            mock_config.QUARANTINE_TOPIC_PATH,
            mock_message.data,
            tx_id=tx_id,
            error=error)

    @patch('app.quarantine.CONFIG')
    def test_quarantine_submission_tx_id_none(self, mock_config):
        mock_message = Mock()
        mock_message.data = "silly message"
        mock_config.QUARANTINE_TOPIC_PATH = "quarantine_path"
        tx_id = None
        error = "bad error"
        quarantine_submission(mock_message, tx_id, error)
        mock_config.QUARANTINE_SEFT_PUBLISHER.publish.assert_called_with(
            mock_config.QUARANTINE_TOPIC_PATH,
            mock_message.data,
            tx_id="No tx_id provided",
            error=error)
