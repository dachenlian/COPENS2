from pathlib import Path
from unittest.mock import create_autospec, patch, Mock, mock_open

from django.test import TestCase
from django.core.files.uploadedfile import UploadedFile

from .. import utils


class SaveFileToDriveTest(TestCase):

    m = mock_open()

    @patch('createcorpora.utils.Path.exists', autospec=True)
    def test_return_none_when_file_exists(self, mocked_exist):
        raw_dir = Path('path/to/test')
        f = create_autospec(UploadedFile)
        f.name = 'test.vrt'
        mocked_exist.return_value = True
        result = utils.save_file_to_drive(f, raw_dir)
        mocked_exist.assert_called_once()
        self.assertIsNone(result)

    @patch('createcorpora.utils.open')
    @patch('createcorpora.utils.Path.exists', autospec=True)
    def test_return_slugified_filename_when_file_does_not_exist(self, mocked_exist, mocked_open):
        raw_dir = Path('path/to/test')
        f = create_autospec(UploadedFile)
        f.name = 'test with spaces.vrt'
        mocked_exist.return_value = False
        result = utils.save_file_to_drive(f, raw_dir)
        mocked_exist.assert_called_once()
        mocked_open.assert_called_once()
        self.assertEqual('test-with-spaces.vrt', result)
