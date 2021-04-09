import unittest
from requests.exceptions import ConnectionError
import requests
from unittest.mock import patch
from requests import Session
from urllib3.exceptions import MaxRetryError

from app.deliver import deliver_seft, post
from app.errors import QuarantinableError, RetryableError


class TestDeliver(unittest.TestCase):
    r = requests.Response()
    seft_message = {
        'tx_id': '0f534ffc-9442-414c-b39f-a756b4adc6cb',
        'filename': 'seft_survey'
    }

    def deliver_bad_response(self, data, byte, exception):
        with self.assertRaises(exception) as submission_exception:
            deliver_seft(data, byte)
        return str(submission_exception.exception)

    def test_deliver_seft(self):
        with patch('app.deliver.post') as mock_post:
            mock_post.return_value = self.r
            self.r.status_code = 200
            self.assertTrue(deliver_seft(self.seft_message, b'this is some bytes'))

    def test_quarantine_error(self):
        quarantine_response = "Bad Request response from sdx-deliver"
        with patch('app.deliver.post') as mock_post:
            mock_post.return_value = self.r
            self.r.status_code = 400
            quarantine_exception_str = self.deliver_bad_response(self.seft_message, b'this is some bytes', RetryableError)
            self.assertEqual(quarantine_exception_str, quarantine_response)

    def test_retry_error(self):
        retry_response = "Bad response from sdx-deliver"
        with patch('app.deliver.post') as mock_post:
            mock_post.return_value = self.r
            self.r.status_code = 500
            retry_exception_str = self.deliver_bad_response(self.seft_message, b'this is some bytes', QuarantinableError)
            self.assertEqual(retry_exception_str, retry_response)

    @patch.object(Session, 'post')
    def test_post(self, mock_response_post):
        filename = "seft_survey"
        seft_message = {
            'tx_id': '0f534ffc-9442-414c-b39f-a756b4adc6cb',
            'filename': 'seft_survey'
        }
        mock_response_post.return_value.status_code = 200
        post(filename, seft_message)
        mock_response_post.assert_called()

    @patch('app.deliver.session')
    def test_post_max_retry_exception(self, mock_session):
        mock_session.post.side_effect = MaxRetryError("pool", "url", "reason")
        filename = "seft_survey"
        seft_message = {
            'tx_id': '0f534ffc-9442-414c-b39f-a756b4adc6cb',
            'filename': 'seft_survey'
        }
        with self.assertRaises(RetryableError):
            post(filename, seft_message)

    @patch('app.deliver.session')
    def test_post_connection_exception(self, mock_session):
        mock_session.post.side_effect = ConnectionError()
        filename = "seft_survey"
        seft_message = {
            'tx_id': '0f534ffc-9442-414c-b39f-a756b4adc6cb',
            'filename': 'seft_survey'
        }
        with self.assertRaises(RetryableError):
            post(filename, seft_message)
