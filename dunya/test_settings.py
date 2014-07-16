from settings import *

INSTALLED_APPS = INSTALLED_APPS + ('django_nose', )
del DATABASES["motif"]
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
