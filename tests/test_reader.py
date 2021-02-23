import unittest
from unittest.mock import patch

from app import BUCKET_NAME, PROJECT_ID
from app.reader import read


class TestReader(unittest.TestCase):

    @patch('app.reader.BUCKET')
    def test_reader(self, mock_storage):
        filename = 'test_file'
        storage_client = mock_storage.Client
        bucket = storage_client(PROJECT_ID).bucket
        blob = bucket(BUCKET_NAME).blob
        data_bytes = blob.download_as_bytes
        read(filename)
        storage_client.assert_called_with(PROJECT_ID)
        bucket.assert_called_with(BUCKET_NAME)
        data_bytes.return_value.decode.return_value = b"file_content"
