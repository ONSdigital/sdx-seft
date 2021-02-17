import unittest
import json
from unittest.mock import patch

from app.collect import process


class TestCollect(unittest.TestCase):

    @patch('app.collect.deliver_seft')
    @patch('app.collect.quarantine_submission')
    @patch('app.collect.read')
    def test_deliver_seft(self, read, quarantine_submission, deliver_seft):
        seft_message = {
            'tx_id': '0f534ffc-9442-414c-b39f-a756b4adc6cb',
            'filename': 'seft_survey'
        }
        data_bytes = b'this is some bytes'
        read.return_value = data_bytes
        process(json.dumps(seft_message))
        deliver_seft.assert_called_with(seft_message, data_bytes)
        quarantine_submission.assert_not_called()

    @patch('app.collect.deliver_seft')
    @patch('app.collect.quarantine_submission')
    @patch('app.collect.read')
    def test_seft_quarantine(self, read, quarantine_submission, deliver_seft):
        seft_message = {
            'tx_id': '0f534ffc-9442-414c-b39f-a756b4adc6cb',
            "filename": "seft_survey"
        }
        message_str = json.dumps(seft_message)
        read.side_effect = Exception()
        process(message_str)
        quarantine_submission.assert_called_with(message_str, seft_message['tx_id'])
