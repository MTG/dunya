from settings import *

INSTALLED_APPS = INSTALLED_APPS + ('django_nose', )
if "motif" in DATABASES:
    del DATABASES["motif"]
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

SOUTH_TESTS_MIGRATE = False

NOSE_ARGS = [
    '--with-xcoverage',
    '--cover-package=carnatic,dashboard,docserver,hindustani,makam',
    '--with-xunit',
    '--cover-erase'
]
