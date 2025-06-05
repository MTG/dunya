import uuid
from unittest import mock

from django.test import TestCase, override_settings

import dashboard.extractors
from docserver import jobs, models


class TestExtractor(dashboard.extractors.ExtractorModule):
    _version = "0.1"
    _sourcetype = "mp3"
    _slug = "asd"
    _many_files = True
    _output = {"pitch": {"extension": "json", "mimetype": "application/json"}}

    def run_many(self, fname):
        return {"pitch": '{"test": "0.1"}'}


class Test2Extractor(dashboard.extractors.ExtractorModule):
    _version = "0.1"
    _sourcetype = "mp3"
    _slug = "asd2"
    _many_files = False
    _output = {"pitch": {"extension": "json", "mimetype": "application/json"}}

    def run(self, mb, fname):
        return {"pitch": '{"test": "0.1"}'}


class AbstractFileTest(TestCase):
    def setUp(self):
        collid = uuid.uuid4()
        self.col1 = models.Collection.objects.create(
            collectionid=collid, name="collection 1", slug="col", root_directory="/tmp/col1"
        )
        self.file_type = models.SourceFileType.objects.create(extension="mp3", name="mp3_file_type", slug="mp3")
        self.doc1 = models.Document.objects.create(title="doc1", external_identifier="111111")
        self.doc1.collections.add(self.col1)
        self.sfile1 = models.SourceFile.objects.create(document=self.doc1, file_type=self.file_type, size=1000)

        self.get_m = mock.Mock()
        self.log = mock.Mock()
        jobs.log = self.log
        jobs._get_module_instance_by_path = self.get_m


class SourceFileTest(AbstractFileTest):
    @mock.patch("os.makedirs")
    @mock.patch("builtins.open")
    def test_run_module_on_collection(self, mock_open, makedir):
        modulepath = "dashboard.extractors.TestExtractor"
        instance = TestExtractor()
        self.get_m.return_value = instance

        mod = jobs.create_module(modulepath, [self.col1.pk])
        self.assertEqual(len(models.Module.objects.all()), 1)

        jobs.process_collection(self.col1.pk, mod.versions.all()[0].pk)
        self.assertEqual(len(models.Document.objects.all()), 2)

    @mock.patch("os.makedirs")
    @mock.patch("builtins.open")
    @override_settings(task_always_eager=True)
    def test_process_document(self, mock_open, makedir):
        # /tmp/col1/incoming/11/111111/asd2/0.1
        modulepath = "dashboard.extractors.Test2Extractor"
        instance = Test2Extractor()
        self.get_m.return_value = instance

        mod = jobs.create_module(modulepath, [self.col1.pk])
        self.assertEqual(len(models.Module.objects.all()), 1)

        jobs.run_module_on_collection(self.col1.pk, mod.pk)

        self.assertEqual(len(self.doc1.derivedfiles.all()), 1)
