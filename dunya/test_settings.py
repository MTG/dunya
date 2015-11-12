from settings import *

if "motif" in DATABASES:
    del DATABASES["motif"]

from xmlrunner.extra.djangotestrunner import XMLTestRunner
from django.test.runner import DiscoverRunner
from django.db import connections, DEFAULT_DB_ALIAS

# We use the XMLTestRunner on CI
#class DunyaTestRunner(XMLTestRunner):
class DunyaTestRunner(DiscoverRunner):
    def setup_databases(self):
        result = super(DunyaTestRunner, self).setup_databases()
        connection = connections[DEFAULT_DB_ALIAS]
        cursor = connection.cursor()
        cursor.execute('CREATE EXTENSION IF NOT EXISTS UNACCENT')
        return result

TEST_RUNNER = "dunya.test_settings.DunyaTestRunner"
TEST_OUTPUT_VERBOSE = True
TEST_OUTPUT_DESCRIPTIONS = True
TEST_OUTPUT_DIR = "xmlrunner"
CELERY_ALWAYS_EAGER = True
