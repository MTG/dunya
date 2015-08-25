from django.test import TestCase
from django.http import QueryDict
from django.contrib.auth.models import Permission
from django.contrib import auth

import mock
from docserver import forms
from docserver import models
from docserver import util
from docserver import jobs
import compmusic.extractors

class TestExtractor(compmusic.extractors.ExtractorModule):
    __version__ = "0.1"
    __sourcetype__ = "mp3"
    __slug__ = "asd"
    __many_files__ = True
    __output__ = {"pitch": {"extension": "json", "mimetype": "application/json"}}
    
    def run(self, fname):
       return {'pitch': '{"test": "0.1"}'}

class Test2Extractor(compmusic.extractors.ExtractorModule):
    __version__ = "0.1"
    __sourcetype__ = "mp3"
    __slug__ = "asd2"
    __many_files__ = False
    __output__ = {"pitch": {"extension": "json", "mimetype": "application/json"}}
    
    def run(self, fname):
       return {'pitch': '{"test": "0.1"}'}

class AbstractFileTest(TestCase):
    def setUp(self):
        self.col1 = models.Collection.objects.create(collectionid="f33f3f73", name="collection 1", slug="col", root_directory="/tmp/col1")
        self.file_type = models.SourceFileType.objects.create(extension="mp3", name="mp3_file_type", slug="mp3")
        self.doc1 = models.Document.objects.create(title="doc1", external_identifier="111111")
        self.doc1.collections.add(self.col1)
        self.sfile1 = models.SourceFile.objects.create(document=self.doc1, file_type=self.file_type, size=1000)

        self.get_m = mock.Mock() 
        self.log = mock.Mock()
        jobs.log = self.log 
        jobs._get_module_instance_by_path = self.get_m

class SourceFileTest(AbstractFileTest):

    @mock.patch('docserver.jobs.process_document')
    def test_run_module_on_collection(self, pd):
        modulepath = "compmusic.extractors.TestExtractor"
        instance = TestExtractor()
        self.get_m.return_value = instance

        mod = jobs.create_module(modulepath, [self.col1.pk])
        self.assertEqual(len(models.Module.objects.all()), 1)

        jobs.run_module_on_collection(self.col1.pk, mod.pk)
        self.assertEqual(len(models.Document.objects.all()), 2)
        
        jobs.run_module_on_collection(self.col1.pk, mod.pk)
    
    @mock.patch('docserver.log.log_processed_file') 
    def test_process_document(self, log):
        modulepath = "compmusic.extractors.TestExtractor"
        instance = TestExtractor()
        self.get_m.return_value = instance

        mod = jobs.create_module(modulepath, [self.col1.pk])
        self.assertEqual(len(models.Module.objects.all()), 1)
        
        jobs.run_module_on_collection(self.col1.pk, mod.pk)

        doc = models.Document.objects.get(pk=self.col1.pk)
        self.assertEqual(len(doc.derivedfiles.all()), 1)
    
    def test_process_document(self):
        modulepath = "compmusic.extractors.Test2Extractor"
        instance = Test2Extractor()
        self.get_m.return_value = instance

        mod = jobs.create_module(modulepath, [self.col1.pk])
        self.assertEqual(len(models.Module.objects.all()), 1)
        
        jobs.run_module_on_collection(self.col1.pk, mod.pk)

        self.assertEqual(len(self.doc1.derivedfiles.all()), 1)

