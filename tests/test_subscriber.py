import unittest
from unittest import mock
from unittest.mock import patch, Mock
from concurrent import futures
from app.errors import RetryableError
from app.subscriber import callback, start
from google.cloud.pubsub_v1.subscriber.message import Message


class TestReader(unittest.TestCase):

    @mock.patch('app.subscriber.process')
    def test_callback(self, mock_process):
        tx_id = "345"
        mock_message = Mock()
        mock_message.attributes.get.return_value = tx_id
        mock_message.data.decode.return_value = 'my message'
        callback(mock_message)
        mock_message.ack.assert_called()

    @patch.object(Message, 'ack')
    @mock.patch('app.subscriber.process')
    @mock.patch('app.subscriber.quarantine_submission')
    def test_retryable_error(self, quarantine_submission, mock_process, mock_message):
        mock_message.attributes = {'tx_id': 'tx_id'}
        mock_process.side_effect = RetryableError()
        callback(mock_message.data)
        quarantine_submission.assert_not_called()

    @mock.patch('app.subscriber.CONFIG')
    def test_start_timeout_error(self, mock_config):
        streaming_pull_future = Mock()
        streaming_pull_future.result = Mock(side_effect=futures.TimeoutError)
        mock_config.SEFT_SUBSCRIBER.subscribe = Mock(return_value=streaming_pull_future)
        start()
        streaming_pull_future.cancel.assert_called()
