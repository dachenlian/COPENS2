import logging
from django.test import TestCase
from django.db.models import Q

from createcorpora.forms import UploadCorpusForm, SearchForm
from createcorpora.models import CopensUser, Corpus
from .. import factories
from ..utils import create_text_file


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


class SearchFormTest(TestCase):
    def setUp(self):
        self.user = factories.UserFactory(username='rich')

    def test_no_corpora_returns_blank_choices(self):
        form = SearchForm(user=self.user)
        self.assertEqual(len(form.DB_CHOICES), 0)

    def test_user_can_only_see_own_and_public_corpora(self):
        factories.CorpusFactory.create_batch(size=10, owner=self.user.copens_user, is_public=True)
        factories.CorpusFactory.create_batch(size=10, owner=self.user.copens_user, is_public=False)
        factories.CorpusFactory.create_batch(size=25, is_public=False)
        factories.CorpusFactory.create_batch(size=25, is_public=True)
        form = SearchForm(user=self.user)
        self.assertEqual(len(form.DB_CHOICES),
                         Corpus.objects.filter(Q(owner=self.user.copens_user) | Q(is_public=True)).count())

