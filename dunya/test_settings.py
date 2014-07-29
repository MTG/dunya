from settings import *

INSTALLED_APPS = INSTALLED_APPS + ('django_nose', )
if "motif" in DATABASES:
    del DATABASES["motif"]
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    '--with-xcoverage',
    '--cover-package=carnatic,dashboard,docserver,hindustani',
    '--with-xunit',
    '--cover-erase'
]
