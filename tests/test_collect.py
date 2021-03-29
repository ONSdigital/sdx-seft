import unittest
import json
from unittest import mock
from unittest.mock import patch

from google.cloud.pubsub_v1.subscriber.message import Message

from app.collect import process
from app.errors import RetryableError, QuarantinableError
from app.subscriber import callback


class TestCollect(unittest.TestCase):

    @patch('app.collect.deliver_seft')
    @patch('app.collect.read')
    def test_deliver_seft(self, read, deliver_seft):
        seft_message = {
            'tx_id': '0f534ffc-9442-414c-b39f-a756b4adc6cb',
            'filename': 'seft_survey'
        }
        data_bytes = b'this is some bytes'
        read.return_value = data_bytes
        process(json.dumps(seft_message))
        deliver_seft.assert_called_with(seft_message, data_bytes)

    @patch('app.subscriber.process')
    @patch('app.subscriber.quarantine_submission')
    def test_retryable_error(self, quarantine_submission, sub_process):
        seft_message = {
            'tx_id': '0f534ffc-9442-414c-b39f-a756b4adc6cb',
            "filename": "seft_survey"
        }
        sub_process(seft_message)
        sub_process.side_effect = RetryableError()
        quarantine_submission.assert_not_called()

    @patch('app.subscriber.process')
    def test_connection_error(self, mock_process):
        seft_message = {
            'tx_id': '0f534ffc-9442-414c-b39f-a756b4adc6cb',
            "filename": "seft_survey"
        }
        mock_process(seft_message)
        mock_process.side_effect = QuarantinableError()
        self.assertRaises(QuarantinableError)

    @patch.object(Message, 'ack')
    @mock.patch('app.subscriber.process', side_effect=Exception(QuarantinableError))
    @mock.patch('app.subscriber.quarantine_submission')
    def test_process(self, mock_quarantine, mock_process, mock_message):
        callback(mock_message)
        mock_quarantine.assert_called()
