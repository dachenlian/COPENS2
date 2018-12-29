"""
Django settings for COPENS project.

Generated by 'django-admin startproject' using Django 2.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
from pathlib import Path
import sys

from django.urls import reverse_lazy
from dotenv import load_dotenv


def show_toolbar(request):
    if request.is_ajax():
        return False
    return True


DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': 'COPENS.settings.base.show_toolbar'
}

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = Path(BASE_DIR).joinpath('web-variables.env')
load_dotenv(dotenv_path=env_path)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',
    # 'allauth.socialaccount.providers.google',

    'copens_static_pages.apps.CopensStaticPagesConfig',
    'createcorpora.apps.CreatecorporaConfig',
    'crispy_forms',
    'django_extensions',
    'django_rq',
    'debug_toolbar',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

RQ_QUEUES = {
    'default': {
        'HOST': 'redis',
        'PORT': 6379,
        'DB': 0,
        'DEFAULT_TIMEOUT': 360,
    },
    'with-sentinel': {
        'SENTINELS': [('redis', 26736), ('redis', 26737)],
        'MASTER_NAME': 'redismaster',
        'DB': 0,
        'SOCKET_TIMEOUT': None,
        'CONNECTION_KWARGS': {
            'socket_connect_timeout': 0.3
        },
    },
}
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

ROOT_URLCONF = 'COPENS.urls'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'memcached:11211',
    },
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

WSGI_APPLICATION = 'COPENS.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'copens',
        'USER': 'copens',
        'PASSWORD': 'copens',
        'HOST': 'copens_db',
        'PORT': 3306,
    }
}

if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:'
        }
    }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} - {levelname} - {name}:{lineno} - {funcName}(): {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        }
    },
    'loggers': {
        'parso': {  # suppress debug info from appearing in shell_plus (IPython)
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        '': {
            'handlers': ['file', 'console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
    },
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Taipei'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

INTERNAL_IPS = ['*']

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

CRISPY_TEMPLATE_PACK = 'bootstrap4'

CWB_REGISTRY_DIR = os.path.join(BASE_DIR, 'cwb', 'registry')
CWB_PUBLIC_REG_DIR = os.path.join(CWB_REGISTRY_DIR, 'public')
CWB_DATA_DIR = os.path.join(BASE_DIR, 'cwb', 'data')
CWB_RAW_DIR = os.path.join(BASE_DIR, 'cwb', 'raw')
CWB_QUERY_RESULTS_DIR = os.path.join(BASE_DIR, 'cwb', 'results')

SITE_ID = 1

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False

LOGIN_REDIRECT_URL = reverse_lazy('create:home')
LOGOUT_REDIRECT_URL = reverse_lazy('copens_static_pages:home')

TCSL_ENDPOINT = os.getenv('TCSL_ENDPOINT')
TCSL_USERNAME = os.getenv('TCSL_USERNAME')
TCSL_PASSWORD = os.getenv('TCSL_PASSWORD')
