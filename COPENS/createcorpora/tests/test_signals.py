from pathlib import Path

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
        self.assertEqual(mocked_signal.call_count, 1)

    @mock.patch.object(signals.Path, 'mkdir', autospec=True)
    @mock.patch.object(signals.Path, 'exists', autospec=True)
    def test_make_directories_succeed(self, mocked_exists, mocked_mkdir):
        username = 'rich'
        mocked_exists.return_value = False
        signals.make_dir(Path(settings.CWB_RAW_DIR) / username)
        self.assertEqual(mocked_mkdir.call_count, 1)

    @mock.patch.object(signals.Path, 'mkdir', autospec=True)
    @mock.patch.object(signals.Path, 'exists', autospec=True)
    def test_make_directories_fail(self, mocked_exists, mocked_mkdir):
        username = 'rich'
        mocked_exists.return_value = True
        signals.make_dir(Path(settings.CWB_RAW_DIR) / username)
        self.assertEqual(mocked_mkdir.call_count, 0)

