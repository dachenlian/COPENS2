import factory
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save

from .models import CopensUser, Corpus


@factory.django.mute_signals(post_save)
class CopensUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CopensUser

    user = factory.SubFactory('createcorpora.factories.UserFactory', copens_user=None)


@factory.django.mute_signals(post_save)
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Faker('name')
    copens_user = factory.RelatedFactory(CopensUserFactory, 'user')


