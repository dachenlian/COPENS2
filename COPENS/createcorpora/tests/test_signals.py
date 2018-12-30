from django.test import TestCase
from django.db.models.signals import post_save
from unittest import mock
from django.contrib.auth import get_user_model


class SignalsTest(TestCase):
    @mock.patch('createcorpora.signals.create_copens_user', autospec=True)
    def test_user_creation_triggers_copens_user_signal(self, mocked_signal):
        post_save.connect(mocked_signal, sender=get_user_model())
        user = get_user_model().objects.create_user(username='rich')
        self.assertTrue(mocked_signal.called)


