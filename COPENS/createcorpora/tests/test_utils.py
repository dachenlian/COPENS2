from pathlib import Path
from unittest.mock import create_autospec, patch, Mock, mock_open

from django.test import TestCase
from django.core.files.uploadedfile import UploadedFile

from .. import utils
from ..models import CopensUser, Corpus
from ..factories import CorpusFactory, CopensUserFactory


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


class DeleteFilesFromDriveTest(TestCase):

    @patch('createcorpora.utils.os.remove', autospec=True)
    @patch('createcorpora.utils.os.unlink', autospec=True)
    def test_files_successfully_deleted(self, mocked_unlink, mocked_remove):
        # user = create_autospec(CopensUser)
        # corpus = create_autospec(Corpus)
        user = CopensUserFactory()
        corpus = CorpusFactory(owner=user, is_public=True)
        print(user, corpus)
        # corpus.file_name = 'test.vrt'
        # corpus.en_name = 'en_test'
        utils.delete_files_from_drive(user, corpus)
        mocked_unlink.assert_called()


class CwbTests(TestCase):

    VRT_FILE = Path('test.vrt')
    DATA_DIR = Path('path/to/data')
    REGISTRY_DIR = Path('path/to/registry')

    @patch('createcorpora.utils.Path.mkdir')
    @patch('createcorpora.utils.Path.exists')
    def test_cwb_encode_make_data_dir_if_not_exists(self, mocked_exists, mocked_mkdir):
        p_attrs = '-P pos'
        s_attrs = '-S s'
        mocked_exists.return_value = False
        utils.cwb_encode(self.VRT_FILE, self.DATA_DIR, self.REGISTRY_DIR, p_attrs, s_attrs)
        mocked_mkdir.assert_called()


class CqpTests(TestCase):

    def test_valid_query_returns_result(self):
        query = '台北'
        corpora = ['asbc', ]
        results = utils.cqp_query(query, corpora=corpora)
        self.assertIsNotNone(results)
        read_results = utils.read_results(list(results.values())[0])
        print("*"*40)
        self.assertTrue(read_results, 'Are there any corpora available publicly?')
        print(read_results)
