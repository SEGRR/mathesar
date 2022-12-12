"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import os
from pathlib import Path

from decouple import Csv, config as decouple_config
from dj_database_url import parse as db_url


# We use a 'tuple' with pipes as delimiters as decople naively splits the global
# variables on commas when casting to Csv()
def pipe_delim(pipe_string):
    # Remove opening and closing brackets
    pipe_string = pipe_string[1:-1]
    # Split on pipe delim
    return pipe_string.split("|")


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "django_property_filter",
    "mathesar",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "mathesar.middleware.CursorClosedHandlerMiddleware",
    "mathesar.middleware.PasswordChangeNeededMiddleware",
    'django_userforeignkey.middleware.UserForeignKeyMiddleware',
    'django_request_cache.middleware.RequestCacheMiddleware',
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "config.context_processors.frontend_settings",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# TODO: Add to documentation that database keys should not be than 128 characters.

# MATHESAR_DATABASES should be of the form '({db_name}|{db_url}), ({db_name}|{db_url})'
# See pipe_delim above for why we use pipes as delimiters
DATABASES = {
    db_key: db_url(url_string)
    for db_key, url_string in decouple_config('MATHESAR_DATABASES', cast=Csv(pipe_delim))
}
DATABASES[decouple_config('DJANGO_DATABASE_KEY')] = decouple_config('DJANGO_DATABASE_URL', cast=db_url)

for db_key, db_dict in DATABASES.items():
    # Engine can be '.postgresql' or '.postgresql_psycopg2'
    if not db_dict['ENGINE'].startswith('django.db.backends.postgresql'):
        raise ValueError(
            f"{db_key} is not a PostgreSQL database. "
            f"{db_dict['ENGINE']} found for {db_key}'s engine."
        )


# pytest-django will create a new database named 'test_{DATABASES[table_db]['NAME']}'
# and use it for our API tests if we don't specify DATABASES[table_db]['TEST']['NAME']
TEST = decouple_config('TEST', default=False, cast=bool)
if TEST:
    for db_key, _ in decouple_config('MATHESAR_DATABASES', cast=Csv(pipe_delim)):
        DATABASES[db_key]['TEST'] = {'NAME': DATABASES[db_key]['NAME']}


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = decouple_config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = decouple_config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = decouple_config('ALLOWED_HOSTS', cast=Csv())

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
# https://docs.djangoproject.com/en/3.1/ref/contrib/staticfiles/

STATIC_URL = "/static/"

# When running with DEBUG=False, the webserver needs to serve files from this location
# python manage.py collectstatic has to be run to collect all static files into this location
# The files need to served in brotli or gzip compressed format
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

# Media files (uploaded by the user)

MEDIA_ROOT = os.path.join(BASE_DIR, '.media/')

MEDIA_URL = "/media/"

# Update Authentication classes, removed BasicAuthentication
# Defaults: https://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication'
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'EXCEPTION_HANDLER':
        'mathesar.exception_handlers.mathesar_exception_handler'
}
FRIENDLY_ERRORS = {
    'FIELD_ERRORS': {
        # By default drf-friendly-errors does contain error codes for ListSerializer type
        'ListSerializer': {
            'required': 2007,
            'null': 2027,
            'invalid_choice': 2083,
            'not_a_list': 2123,
            'empty': 2093
        },
        'PermittedPkRelatedField': {
            'required': 2007,
            'null': 2027,
            'does_not_exist': 2151,
            'incorrect_type': 2161
        },
        'PermittedSlugRelatedField': {
            'required': 2007, 'invalid': 2002, 'null': 2027,
            'does_not_exist': 2151, 'incorrect_type': 2161
        },
    },
    'EXCEPTION_DICT': {
        'Http404': 4005
    }
}
# Mathesar settings
MATHESAR_MODE = decouple_config('MODE', default='PRODUCTION')
MATHESAR_UI_BUILD_LOCATION = os.path.join(BASE_DIR, 'mathesar/static/mathesar/')
MATHESAR_MANIFEST_LOCATION = os.path.join(MATHESAR_UI_BUILD_LOCATION, 'manifest.json')
MATHESAR_CLIENT_DEV_URL = 'http://localhost:3000'
MATHESAR_UI_SOURCE_LOCATION = os.path.join(BASE_DIR, 'mathesar_ui/')
MATHESAR_CAPTURE_UNHANDLED_EXCEPTION = decouple_config('CAPTURE_UNHANDLED_EXCEPTION', default=False)

# UI source files have to be served by Django in order for static assets to be included during dev mode
# https://vitejs.dev/guide/assets.html
# https://vitejs.dev/guide/backend-integration.html
STATICFILES_DIRS = [MATHESAR_UI_SOURCE_LOCATION] if MATHESAR_MODE == 'DEVELOPMENT' else [MATHESAR_UI_BUILD_LOCATION]

# Accounts
AUTH_USER_MODEL = 'mathesar.User'
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'
DRF_ACCESS_POLICY = {
    'reusable_conditions': ['mathesar.api.permission_conditions']
}
