import unittest
from unittest.mock import patch

from app.reader import read


class TestReader(unittest.TestCase):

    @patch('app.reader.BUCKET')
    def test_reader(self, mock_bucket):
        filename = 'test_file'
        blob = mock_bucket.blob
        data_bytes = blob.download_as_bytes
        read(filename)
        blob.assert_called_with(f"/{filename}")
        data_bytes.return_value.decode.return_value = b"file_content"
