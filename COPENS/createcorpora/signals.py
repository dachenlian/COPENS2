from pathlib import Path
import logging

from django.contrib.auth.models import User
from django.conf import settings
from .models import CopensUser
from django.db.models.signals import post_save
from django.dispatch import receiver


logger = logging.getLogger('django')


def make_dir(path: Path) -> Path:
    directory = path
    if not directory.exists():
        directory.mkdir()
        return directory
    else:
        print('Directory already exists')
        return directory


@receiver(post_save, sender=User)
def create_copens_user(sender, instance, created, **kwargs):

    logging.info('User created signal received.')
    raw_dir = make_dir(Path(settings.CWB_RAW_DIR) / instance.username)
    data_dir = make_dir(Path(settings.CWB_DATA_DIR) / instance.username)
    registry_dir = make_dir(Path(settings.CWB_REGISTRY_DIR) / instance.username)

    if created:
        CopensUser.objects.create(
            user=instance,
            raw_dir=raw_dir,
            data_dir=data_dir,
            registry_dir=registry_dir,
        )

    logging.info('CopensUser created.')
