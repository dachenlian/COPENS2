from .base import *


DEBUG = True

MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

INSTALLED_APPS += ['debug_toolbar']

