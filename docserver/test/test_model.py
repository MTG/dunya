import uuid

from django.test import TestCase

from docserver import exceptions
from docserver import models
from docserver import util


class TestDocument(TestCase):
    fixtures = ['docserver_sourcefiletype']

    def setUp(self):
        docid = str(uuid.uuid4())
        self.doc = models.Document.objects.create(external_identifier=docid)

    def test_get_file_sourcefile(self):
        sft = models.SourceFileType.objects.get(slug="mp3")

        sf = models.SourceFile.objects.create(file_type=sft, document=self.doc, size=1, path="/foo/source.mp3")

        res = self.doc.get_file("mp3")

        self.assertEqual(res, sf)

    def test_get_file_no_sourcefile(self):
        """ If the argument is a sourcefiletype, but this document doesn't have a sf of that type"""

        with self.assertRaises(exceptions.NoFileException) as cm:
            res = self.doc.get_file("csv")
        self.assertEqual(cm.exception.message, "Looks like a sourcefile, but I can't find one")

    def test_get_derived_slug_no_exist(self):
        """ A slug that doesn't match any sourcefiletype or moduleslug """

        with self.assertRaises(exceptions.NoFileException) as cm:
            res = self.doc.get_file("foo")
        self.assertEqual(cm.exception.message, "Cannot find a module with type foo")

    def test_get_derived_slug_noversion(self):
        """ A module has no versions, or doesn't have the version which is asked for """
        sft = models.SourceFileType.objects.get(slug="mp3")

        module = models.Module.objects.create(slug="derived", source_type=sft)
        modver = models.ModuleVersion.objects.create(module=module, version="0.1")

        noversion = models.Module.objects.create(slug="dernover", source_type=sft)

        with self.assertRaises(exceptions.NoFileException) as cm:
            res = self.doc.get_file("derived", version="0.2")
        self.assertEqual(cm.exception.message, "No known versions for this module")

        with self.assertRaises(exceptions.NoFileException) as cm:
            res = self.doc.get_file("dernover")
        self.assertEqual(cm.exception.message, "No known versions for this module")

    def test_get_derived_with_version(self):
        # with two versions, if the most recent doesn't have anything, use older one
        sft = models.SourceFileType.objects.get(slug="mp3")

        module = models.Module.objects.create(slug="derived", source_type=sft)
        modver1 = models.ModuleVersion.objects.create(module=module, version="0.1", date_added="2016-12-01T00:01:11+00")
        modver2 = models.ModuleVersion.objects.create(module=module, version="0.2", date_added="2016-12-01T10:20:11+00")

        df = models.DerivedFile.objects.create(document=self.doc, module_version=modver1, outputname="info",
                                               extension="json", mimetype="text/plain", num_parts=1)

        res = self.doc.get_file("derived", "info")
        self.assertEqual(res, df)

        # explicit version works too
        res2 = self.doc.get_file("derived", "info", version="0.1")
        self.assertEqual(res2, df)

        # explicit version which has no derived parts results in an error
        with self.assertRaises(exceptions.NoFileException) as cm:
            res3 = self.doc.get_file("derived", "info", version="0.2")
        self.assertEqual(cm.exception.message, "No derived files with this type/subtype or version")

        # No version, but an unknown subtype
        with self.assertRaises(exceptions.NoFileException) as cm:
            res3 = self.doc.get_file("derived", "nothing")
        self.assertEqual(cm.exception.message, "No derived files with this type/subtype")

    def test_get_derived_with_subtype(self):
        sft = models.SourceFileType.objects.get(slug="mp3")

        module = models.Module.objects.create(slug="derived", source_type=sft)
        modver1 = models.ModuleVersion.objects.create(module=module, version="0.1", date_added="2016-12-01T00:01:11+00")

        df = models.DerivedFile.objects.create(document=self.doc, module_version=modver1, outputname="info",
                                               extension="json", mimetype="text/plain", num_parts=1)

        # if the derived file has only one type, make sure it's explicit otherwise an error is returned
        with self.assertRaises(exceptions.NoFileException) as cm:
            res = self.doc.get_file("derived")
        self.assertEqual(cm.exception.message, "This module has only one subtype which you must specify (info)")

        # if a derived file has multiple outputnames/subtypes, an error if not set
        df2 = models.DerivedFile.objects.create(document=self.doc, module_version=modver1, outputname="data",
                                                extension="json", mimetype="text/plain", num_parts=1)

        with self.assertRaises(exceptions.TooManyFilesException) as cm:
            res = self.doc.get_file("derived")
        self.assertEqual(cm.exception.message,
                         "Found more than 1 subtype for this module but you haven't specified what you want")

        # ...otherwise return the correct item
        res2 = self.doc.get_file("derived", "info")
        self.assertEqual(res2, df)

        res3 = self.doc.get_file("derived", "data")
        self.assertEqual(res3, df2)

    def test_get_derived_parts(self):
        sft = models.SourceFileType.objects.get(slug="mp3")

        module = models.Module.objects.create(slug="derived", source_type=sft)
        modver1 = models.ModuleVersion.objects.create(module=module, version="0.1", date_added="2016-12-01T00:01:11+00")

        df = models.DerivedFile.objects.create(document=self.doc, module_version=modver1, outputname="info",
                                               extension="json", mimetype="text/plain", num_parts=3)

        # If the derived file has multiple parts and part not set, error
        with self.assertRaises(exceptions.TooManyFilesException) as cm:
            res = self.doc.get_file("derived", "info")
        self.assertEqual(cm.exception.message, "Found more than 1 part without part set")

        # If part isn't a number, error
        with self.assertRaises(exceptions.NoFileException) as cm:
            res = self.doc.get_file("derived", "info", part="x")
        self.assertEqual(cm.exception.message, "Invalid part")

        # part param is greater than numparts in the file
        with self.assertRaises(exceptions.NoFileException) as cm:
            res = self.doc.get_file("derived", "info", part="6")
        self.assertEqual(cm.exception.message, "Invalid part")

        # derived file which has no parts, error
        df2 = models.DerivedFile.objects.create(document=self.doc, module_version=modver1, outputname="noparts",
                                                extension="json", mimetype="text/plain", num_parts=0)

        with self.assertRaises(exceptions.NoFileException) as cm:
            res = self.doc.get_file("derived", "noparts", part="0")
        self.assertEqual(cm.exception.message, "No parts on this file")


class TestUrlsAndPaths(TestCase):
    fixtures = ['docserver_sourcefiletype']

    def setUp(self):
        docid = "f522f7c6-8299-44e9-889f-063d37526801"
        collid = "7a99e6f3-7d5e-4577-a07d-43605d5b4220"
        coll = models.Collection.objects.create(collectionid=collid,
                                                name="Test collection", slug="test-collection", description="",
                                                root_directory="/collectionroot")
        self.doc = models.Document.objects.create(external_identifier=docid)
        self.doc.collections.add(coll)
        sft = models.SourceFileType.objects.get(slug="mp3")
        self.sf = models.SourceFile.objects.create(file_type=sft, document=self.doc, size=1, path="foo/source.mp3")

        module = models.Module.objects.create(slug="derived", source_type=sft)
        modver = models.ModuleVersion.objects.create(module=module, version="0.1", date_added="2016-12-01T00:01:11+00")
        self.df = models.DerivedFile.objects.create(document=self.doc, module_version=modver, outputname="meta",
                                                    extension="json", mimetype="text/plain", num_parts=2)

    def test_sourcefile_absolute_url(self):
        url = self.sf.get_absolute_url()
        self.assertEqual("/document/by-id/f522f7c6-8299-44e9-889f-063d37526801/mp3", url)

        urlmp3 = self.sf.get_absolute_url("ds-download-mp3")
        self.assertEqual("/document/by-id/f522f7c6-8299-44e9-889f-063d37526801.mp3", urlmp3)

    def test_sourcefile_path(self):
        pathmp3 = self.sf.fullpath
        self.assertEqual("/collectionroot/audio/foo/source.mp3", pathmp3)

    def test_derived_file_absolute_url(self):
        urlder = self.df.get_absolute_url(partnumber=2)
        self.assertEqual("/document/by-id/f522f7c6-8299-44e9-889f-063d37526801/derived?v=0.1&subtype=meta&part=2",
                         urlder)

    def test_derived_file_path(self):
        pathder = self.df.full_path_for_part(1)
        self.assertEqual(
            "/collectionroot/derived/f5/f522f7c6-8299-44e9-889f-063d37526801/derived/0.1/f522f7c6-8299-44e9-889f-063d37526801-derived-0.1-meta-1.json",
            pathder)

        with self.assertRaises(exceptions.NoFileException) as cm:
            pathder = self.df.full_path_for_part(3)
        self.assertEqual(cm.exception.message, "partnumber is greater than number of parts")

        pathder2 = util.docserver_get_filename("f522f7c6-8299-44e9-889f-063d37526801", "derived", "meta", "2")
        self.assertEqual(
            "/collectionroot/derived/f5/f522f7c6-8299-44e9-889f-063d37526801/derived/0.1/f522f7c6-8299-44e9-889f-063d37526801-derived-0.1-meta-2.json",
            pathder2)
