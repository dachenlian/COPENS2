from unittest import mock
from unittest.mock import create_autospec

from django.test import TestCase
from django.core.files.uploadedfile import UploadedFile

from .. import utils
from ..utils import create_text_file


class SaveFileToDriveTest(TestCase):

    @mock.patch('createcorpora.utils.Path', autospec=True)
    def test_return_none_when_file_exists(self, mocked_path):
        raw_dir = mock.Mock()
        f = create_autospec(UploadedFile)
        f.name = 'test.vrt'

        # f = create_text_file('test.vrt')
        mocked_path.exists.return_value = False
        result = utils.save_file_to_drive(f, raw_dir)
        self.assertIsNone(result)
