from django.test import TestCase

from ..models import Corpus
from .. import factories


class TestCopensUser(TestCase):
    def setUp(self):
        self.user = factories.UserFactory()

    def test_copens_user_is_created(self):
        self.assertIsNotNone(self.user.copens_user)


class TestCorpus(TestCase):
    def test_corpus_is_created(self):
        corpus = factories.CorpusFactory()
        self.assertIn(corpus.en_name, str(corpus))

