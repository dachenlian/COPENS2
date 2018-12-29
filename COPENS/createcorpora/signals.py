"""
Contains signals related to user creation.
"""

import logging
from pathlib import Path

from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CopensUser

logger = logging.getLogger(__name__)


def make_dir(path: Path) -> Path:
    """
    Creates a directory provided by path of it does not exist.
    :param path: A system path
    :return: A Path object representing a newly created or existing path.
    """
    directory = path
    if not directory.exists():
        directory.mkdir()
        return directory
    else:
        logger.debug('Directory already exists')
        return directory


@receiver(post_save, sender=User)
def create_copens_user(sender, instance, created: bool, **kwargs) -> None:
    """
    A CopensUser is created when a created signal is sent by a User.
    :param sender: The type of object that sent the signal
    :param instance: An instance of the type of object
    :param created: True if an object was created
    :param kwargs:
    :return: None
    """

    logging.debug('User created signal received.')

    if created:
        raw_dir = make_dir(Path(settings.CWB_RAW_DIR) / instance.username)
        data_dir = make_dir(Path(settings.CWB_DATA_DIR) / instance.username)
        registry_dir = make_dir(Path(settings.CWB_REGISTRY_DIR) / instance.username)

        CopensUser.objects.create(
            user=instance,
            raw_dir=raw_dir,
            data_dir=data_dir,
            registry_dir=registry_dir,
        )

    logging.debug('CopensUser created.')
