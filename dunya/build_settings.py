# Django settings for dunya project.


import os

from django.core.exceptions import ImproperlyConfigured
import dj_database_url
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
import manifest_loader.loaders


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "buildtestkeybuildtestkey"

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',
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
    'manifest_loader',
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
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Dunya middleware
    # Say if the current user is allowed to see bootleg recordings
    'dunya.middleware.ShowBootlegMiddleware',
]

ROOT_URLCONF = 'dunya.urls'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

# collectstatic puts static files here
STATIC_ROOT = '/static/'


class CRAManifestLoader(manifest_loader.loaders.DefaultLoader):
    @staticmethod
    def get_single_match(manifest, key):
        return manifest.get("files", {}).get(key, key)


STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'build')
]

MANIFEST_LOADER = {
    'manifest_file': 'asset-manifest.json',
    'loader': CRAManifestLoader
}


DEBUG = False
