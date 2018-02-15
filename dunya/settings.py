# Django settings for dunya project.


import os

from django.core.exceptions import ImproperlyConfigured
import dj_database_url
import raven


def get_env(envname):
    return os.getenv(envname)


def get_check_env(envname):
    var = get_env(envname)
    if not var:
        raise ImproperlyConfigured("{} is not set".format(envname))
    return var


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_check_env('DUNYA_SECRET_KEY')

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.postgres',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'raven.contrib.django.raven_compat',
    'data',
    'carnatic',
    'dashboard',
    'docserver',
    'account',
    'makam',
    'dunya',
    'hindustani',
    'motifdiscovery',
    'andalusian',
    'jingju',
    'frontend',
    'social_django',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Dunya middleware
    # Log every page that people go to
    'dunya.middleware.PageLoggerMiddleware',
    # Say if the current user is allowed to see bootleg recordings
    'dunya.middleware.ShowBootlegMiddleware',
]

ROOT_URLCONF = 'dunya.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'dunya.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

default_url = 'postgres://postgres@db/postgres'
DATABASES = {'default': dj_database_url.config('DUNYA_DATABASE_URL', default=default_url)}


AUTHENTICATION_BACKENDS = [
    'social_core.backends.twitter.TwitterOAuth',
    'django.contrib.auth.backends.ModelBackend',
]

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators
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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Madrid'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

# collectstatic puts static files here
STATIC_ROOT = '/static/'

SITE_ID = 1

LOGIN_URL = '/social/login/'

# Admins should be in this format:
# Name;email,Name2;email2
admin_str = get_env('DUNYA_ADMINS')
ADMINS = [tuple(s.split(';')) for s in admin_str.split(',')]

MANAGERS = []

deploy_env = get_check_env('DUNYA_DEPLOY_ENV')
if deploy_env == 'prod':
    ALLOWED_HOSTS = ['dunya.compmusic.upf.edu', 'asplab-web3.s.upf.edu']
    debug = False

    #  Sendfile, for serving static content
    SENDFILE_BACKEND = 'sendfile.backends.nginx'
    SENDFILE_ROOT = '/'
    SENDFILE_URL = '/serve'

    RAVEN_CONFIG = {
        'dsn': get_check_env('DUNYA_RAVEN_DSN'),
        'release': raven.fetch_git_sha(os.path.dirname(os.pardir)),
    }
else:  # development
    ALLOWED_HOSTS = []
    debug = True
    SENDFILE_BACKEND = 'sendfile.backends.development'

    # For development this sets up a dummy email server
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = '/tmp/dunya-messages'

    INTERNAL_IPS = ['127.0.0.1']

    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]

DEBUG = debug


# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = '/media'
DERIVED_FOLDER = 'derived'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Header check to see if we are on HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Django rest framework
REST_FRAMEWORK = {
    'PAGE_SIZE': 100,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# To store history/log of output from workers
WORKER_REDIS_HOST = get_check_env('DUNYA_WORKER_REDIS_HOST')

#  Celery

BROKER_URL = get_check_env('DUNYA_CELERY_BROKER_URL')
CELERY_RESULT_DBURI = get_check_env('DUNYA_CELERY_RESULT_URL')

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

class DunyaRouter(object):
    def route_for_task(self, task, *args, **kwargs):
        if task.startswith("dashboard."):
            return {"queue": "import"}
        return {"queue": "celery"}


CELERY_ROUTES = (DunyaRouter(), )
CELERYD_CONCURRENCY = 3


# Notification emails (e.g. account activated)
# Who emails are from
NOTIFICATION_EMAIL_FROM = get_check_env('DUNYA_NOTIFICATION_FROM')
# Who gets system emails (e.g., new user) [list/set]
NOTIFICATION_EMAIL_TO = get_check_env('DUNYA_NOTIFICATION_TO').split(',')


EXTERNAL_OAUTH_LOGIN = ['twitter']
SOCIAL_AUTH_TWITTER_KEY = get_env('DUNYA_TWITTER_KEY')
SOCIAL_AUTH_TWITTER_SECRET = get_env('DUNYA_TWITTER_SECRET')


# Fixed versions of extracted features to show on dunya
FEAT_VERSION_NORMALISED_PITCH = "0.6"
FEAT_VERSION_HINDUSTANI_NORMALISED_PITCH = "0.1"
FEAT_VERSION_CARNATIC_NORMALISED_PITCH = "0.1"
FEAT_VERSION_TONIC = "0.1"
FEAT_VERSION_RHYTHM = "0.3"
FEAT_VERSION_IMAGE = "0.2"
