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


@factory.django.mute_signals(post_save)
class CorpusFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Corpus

    owner = factory.SubFactory(CopensUserFactory)
    en_name = factory.Faker('word')
    zh_name = factory.Faker('word', locale='zh-TW')
    file_name = factory.Faker('file_name', extension='vrt')
    is_public = factory.Faker('boolean', chance_of_getting_true=50)
    date_uploaded = factory.Faker('date_time')
    tcsl_doc_id = factory.Faker('uuid4')
    tcsl_corpus_name = factory.Faker('word')

