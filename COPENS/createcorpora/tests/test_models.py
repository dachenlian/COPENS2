from django.test import TestCase
from ..factories import UserFactory


class TestCopensUser(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_copens_user_is_created(self):
        self.assertIsNotNone(self.user.copens_user)
