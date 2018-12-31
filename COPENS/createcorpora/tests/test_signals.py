from django.test import TestCase
from django.db.models.signals import post_save
from unittest import mock
from django.contrib.auth import get_user_model

from django.conf import settings
from .. import signals


class SignalsTest(TestCase):
    @mock.patch('createcorpora.signals.create_copens_user', autospec=True)
    def test_user_creation_triggers_copens_user_signal(self, mocked_signal):
        post_save.connect(mocked_signal, sender=get_user_model())
        user = get_user_model().objects.create_user(username='rich')
        self.assertTrue(mocked_signal.called)

    @mock.patch('createcorpora.signals.pathlib.Path')
    def test_make_directories_succeed(self):
        username = 'rich'
        self.assertIsNone(signals.make_dir())
        user = get_user_model().objects.create_user(username='rich')
        self.assertIsNotNone()

