# Django settings for dunya project.

import os
from pathlib import Path

import dj_database_url
import manifest_loader.loaders
import sentry_sdk
from django.core.exceptions import ImproperlyConfigured
from sentry_sdk.integrations.django import DjangoIntegration


def get_env(envname):
    return os.getenv(envname)


def get_check_env(envname):
    var = get_env(envname)
    if not var:
        raise ImproperlyConfigured(f"{envname} is not set")
    return var


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_check_env("DUNYA_SECRET_KEY")

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.postgres",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "manifest_loader",
    "data",
    "carnatic",
    "dashboard",
    "docserver",
    "account",
    "makam",
    "dunya",
    "hindustani",
    "motifdiscovery",
    "andalusian",
    "jingju",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Dunya middleware
    # Say if the current user is allowed to see bootleg recordings
    "dunya.middleware.ShowBootlegMiddleware",
]

ROOT_URLCONF = "dunya.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = "dunya.wsgi.application"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

default_url = "postgres://postgres@db/postgres"
DATABASES = {"default": dj_database_url.config("DUNYA_DATABASE_URL", default=default_url)}
if get_env("DUNYA_MOTIF_DB_URL"):
    DATABASES["motif"] = dj_database_url.config("DUNYA_MOTIF_DB_URL")


AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators
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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Madrid"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = "/static/"

# collectstatic puts static files here
STATIC_ROOT = BASE_DIR / "staticfiles"


class CRAManifestLoader(manifest_loader.loaders.DefaultLoader):
    @staticmethod
    def get_single_match(manifest, key):
        entry = manifest.get("files", {}).get(key, key)
        if entry.startswith("/"):
            return entry[1:]
        return entry


STATICFILES_DIRS = [os.path.join(BASE_DIR, "build")]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MANIFEST_LOADER = {"manifest_file": "asset-manifest.json", "loader": CRAManifestLoader}

SITE_ID = 1

LOGIN_URL = "/user/login/"
LOGOUT_REDIRECT_URL = "main"

# Admins should be in this format:
# Name;email,Name2;email2
admin_str = get_env("DUNYA_ADMINS")
ADMINS = [tuple(s.split(";")) for s in admin_str.split(",") if s]

MANAGERS = []

deploy_env = get_check_env("DUNYA_DEPLOY_ENV")
if deploy_env == "prod":
    USE_X_FORWARDED_HOST = True
    # Host 'nginx' is for services inside docker to connect
    # directly to dunya.
    ALLOWED_HOSTS = ["dunya.compmusic.upf.edu", "dunya.upf.edu", "dunya.mtg.sb.upf.edu", "nginx"]
    debug = False

    #  Sendfile, for serving static content
    SENDFILE_BACKEND = "django_sendfile.backends.nginx"
    SENDFILE_ROOT = "/"
    SENDFILE_URL = "/serve"

    SENTRY_DSN = get_check_env("DUNYA_SENTRY_DSN")
    sentry_sdk.init(dsn=SENTRY_DSN, integrations=[DjangoIntegration()], send_default_pii=True)
    GMAIL_SEND_EMAIL = True
else:  # development
    ALLOWED_HOSTS = ["localhost", "web"]
    debug = True
    SENDFILE_BACKEND = "django_sendfile.backends.development"

    # For development this sets up a dummy email server
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    EMAIL_FILE_PATH = "/tmp/dunya-messages"

    INTERNAL_IPS = ["127.0.0.1"]

    INSTALLED_APPS += [
        "debug_toolbar",
    ]

    MIDDLEWARE = [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ] + MIDDLEWARE
    GMAIL_SEND_EMAIL = True

DEBUG = debug


# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = "/media"
DERIVED_FOLDER = "derived"

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = "/media/"

# Header check to see if we are on HTTPS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Django rest framework
REST_FRAMEWORK = {
    "PAGE_SIZE": 100,
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        }
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
    },
}

# To store history/log of output from workers
WORKER_REDIS_HOST = get_check_env("DUNYA_WORKER_REDIS_HOST")

#  Celery

CELERY_BROKER_URL = get_check_env("DUNYA_CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = get_check_env("DUNYA_CELERY_RESULT_URL")

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"


class DunyaRouter:
    def route_for_task(self, task, *args, **kwargs):
        if task.startswith("dashboard."):
            return {"queue": "import"}
        return {"queue": "celery"}


CELERY_TASK_ROUTES = (DunyaRouter(),)
CELERY_WORKER_CONCURRENCY = 3


# Notification emails (e.g. account activated)
# Who emails are from
NOTIFICATION_EMAIL_FROM = get_check_env("DUNYA_NOTIFICATION_FROM")
# Who gets system emails (e.g., new user) [list/set]
NOTIFICATION_EMAIL_TO = get_check_env("DUNYA_NOTIFICATION_TO").split(",")


# Fixed versions of extracted features to show on dunya
FEAT_VERSION_NORMALISED_PITCH = "0.6"
FEAT_VERSION_HINDUSTANI_NORMALISED_PITCH = "0.1"
FEAT_VERSION_CARNATIC_NORMALISED_PITCH = "0.1"
FEAT_VERSION_TONIC = "0.1"
FEAT_VERSION_RHYTHM = "0.3"
FEAT_VERSION_IMAGE = "0.2"
