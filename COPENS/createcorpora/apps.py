from django.apps import AppConfig


class CreatecorporaConfig(AppConfig):
    name = 'createcorpora'

    def ready(self):
        import createcorpora.signals  # noqa
