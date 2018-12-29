import logging
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

from createcorpora.forms import UploadCorpusForm, SearchForm
from createcorpora.models import CopensUser, Corpus
from ..factories import UserFactory

logger = logging.getLogger(__name__)


def create_text_file(name):
    f = {
        'file': SimpleUploadedFile(name=name, content=bytes('測試資料', encoding='utf8'))
    }
    return f


class UploadCorpusFormTest(TestCase):
    def test_valid_data(self):
        file = create_text_file('test.vrt')
        form = UploadCorpusForm({
            'zh_name': '中研院平衡語料庫',
            'en_name': 'ASBC',
            'needs_preprocessing': False,
            'is_public': False,
            'positional_attrs': '-P pos',
            'structural_attrs': '-S s'
        }, file)
        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEqual(form.cleaned_data.get('zh_name'), '中研院平衡語料庫')
        self.assertEqual(form.cleaned_data.get('en_name'), 'ASBC')
        self.assertEqual(form.cleaned_data.get('file').name, 'test.vrt')
        self.assertFalse(form.cleaned_data.get('needs_preprocessing'))
        self.assertFalse(form.cleaned_data.get('is_public'))
        self.assertEqual(form.cleaned_data.get('positional_attrs'), '-P pos')
        self.assertEqual(form.cleaned_data.get('structural_attrs'), '-S s')

    def test_invalid_data(self):
        file = create_text_file('測試.vrt')
        form = UploadCorpusForm({
            'zh_name': '中研院平衡語料庫',
            'en_name': 'ASBC',
            'needs_preprocessing': False,
            'is_public': False,
            'positional_attrs': 'P pos',
            'structural_attrs': 'S s'
        }, file)
        self.assertFalse(form.is_valid(), msg=form.errors)
        self.assertEqual(form['file'].errors,
                         ["You may only use the characters A to Z, 0 to 9, and simple punctuation in your password."])
        self.assertEqual(form['positional_attrs'].errors,
                         ["Positional attributes must begin with -P"])
        self.assertEqual(form['structural_attrs'].errors,
                         ["Structural attributes must begin with -S"])


# class SearchFormTest(TestCase):
    # def setUp(self):
    #     user = UserFactory()
    #
    #     Corpus.objects.create(
    #
    #     )

