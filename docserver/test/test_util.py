from django.test import TestCase
import mock
import uuid
from StringIO import StringIO

from docserver import util
from docserver import models

class UtilTest(TestCase):

    fixtures = ['docserver_sourcefiletype']

    def setUp(self):
        self.u = str(uuid.uuid4())
        self.root = "/root/directory"

        self.coll = models.Collection.objects.create(collectionid=self.u, name='test collection',
                slug='test-collection', description='', root_directory=self.root)
        self.doc = models.Document.objects.create(external_identifier="1122-3333-4444")
        self.doc.collections.add(self.coll)
        self.sft = models.SourceFileType.objects.get_by_slug("mp3")
    
    def test_get_root_dir(self):
        self.assertEqual(self.doc.get_root_dir(), "/root/directory")


    @mock.patch('os.makedirs')
    @mock.patch('docserver.util._write_to_disk')
    @mock.patch('docserver.util.docserver_add_sourcefile')
    def test_upload_and_save_file_audio(self, add_sourcefile, write, makedirs):

        thefile = StringIO()

        util.docserver_upload_and_save_file(self.doc.id, self.sft.id, thefile)
        final_filename = "/root/directory/audio/11/1122-3333-4444/mp3/1122-3333-4444-mp3.mp3"
        write.assert_called_with(thefile, final_filename)
        makedirs.assert_called_with("/root/directory/audio/11/1122-3333-4444/mp3")
        add_sourcefile.assert_called_with(self.doc.id, self.sft.id, final_filename)

    @mock.patch('os.makedirs')
    @mock.patch('docserver.util._write_to_disk')
    @mock.patch('docserver.util.docserver_add_sourcefile')
    def test_upload_and_save_file_data(self, add_sourcefile, write, makedirs):

        thefile = StringIO()

        othersft = models.SourceFileType.objects.get_by_slug("csv")
        util.docserver_upload_and_save_file(self.doc.id, othersft.id, thefile)
        final_filename = "/root/directory/data/11/1122-3333-4444/csv/1122-3333-4444-csv.csv"
        write.assert_called_with(thefile, final_filename)
        makedirs.assert_called_with("/root/directory/data/11/1122-3333-4444/csv")
        add_sourcefile.assert_called_with(self.doc.id, othersft.id, final_filename)

    @mock.patch('os.stat')
    def test_add_sourcefile(self, stat):
        m = mock.Mock()
        stat.return_value = m
        m.st_size = 100

        sft = models.SourceFileType.objects.get_by_slug("mp3")
        final_filename = "/root/directory/audio/11/1122-3333-4444/mp3/1122-3333-4444-mp3.mp3"
        sf, created = util.docserver_add_sourcefile(self.doc.id, self.sft.id, final_filename)

        self.assertTrue(created)
        stat.assert_called_with(final_filename)
        self.assertEqual(self.doc, sf.document)
        self.assertEqual(sft, sf.file_type)
        self.assertEqual("11/1122-3333-4444/mp3/1122-3333-4444-mp3.mp3", sf.path)

    @mock.patch('os.stat')
    def test_add_sourcefile_relative_path(self, stat):
        m = mock.Mock()
        stat.return_value = m
        m.st_size = 100

        final_filename = "audio/11/1122-3333-4444/mp3/1122-3333-4444-mp3.mp3"
        sf, created = util.docserver_add_sourcefile(self.doc.id, self.sft.id, final_filename)
        self.assertEqual("audio/11/1122-3333-4444/mp3/1122-3333-4444-mp3.mp3", sf.path)

    @mock.patch('os.stat')
    def test_add_sourcefile_already_exists(self, stat):

        final_filename = "audio/11/1122-3333-4444/mp3/1122-3333-4444-mp3.mp3"
        sf = models.SourceFile.objects.create(path=final_filename, size=100, document=self.doc, file_type=self.sft)
        sfid = sf.id

        m = mock.Mock()
        stat.return_value = m
        m.st_size = 200

        new_filename = "/root/directory/audio/something-else.mp3"
        newsf, created = util.docserver_add_sourcefile(self.doc.id, self.sft.id, new_filename)

        self.assertFalse(created)
        self.assertEqual("something-else.mp3", newsf.path)
        self.assertEqual(200, newsf.size)
        self.assertEqual(sfid, newsf.id)
