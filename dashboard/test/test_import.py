from django.test import TestCase

import mock
import uuid

from dashboard import models
from dashboard import jobs

class CollectionTest(TestCase):
    def setUp(self):
        u = str(uuid.uuid4())
        self.collection = models.Collection.objects.create(collectionid=u, name="Test collection", root_directory="/a/directory")
        self.directory = models.CollectionDirectory.objects.create(collection=self.collection, path="subdir")

        self.file1id = str(uuid.uuid4())
        self.file1 = models.CollectionFile.objects.create(name="one.mp3", directory=self.directory, recordingid=self.file1id)
        self.file2id = str(uuid.uuid4())
        self.file2 = models.CollectionFile.objects.create(name="two.mp3", directory=self.directory, recordingid=self.file2id)

    @mock.patch("compmusic.file_metadata")
    @mock.patch("os.listdir")
    def test_check_existing_dirs_file_removed(self, listdir, meta):
        listdir.return_value = ["one.mp3"]
        meta.return_value = {"meta": {"recordingid": self.file1id}}

        self.assertEqual(2, len(self.directory.collectionfile_set.all()))
        jobs._check_existing_directories(self.collection)

        self.assertEqual(1, len(self.directory.collectionfile_set.all()))

    @mock.patch("compmusic.file_metadata")
    @mock.patch("dashboard.jobs._match_directory_to_release")
    @mock.patch("os.listdir")
    def test_check_existing_dirs_file_added(self, listdir, match, meta):
        listdir.return_value = ["one.mp3", "two.mp3", "three.mp3"]
        ids = {"/a/directory/subdir/one.mp3": {"meta": {"recordingid": self.file1id}},
                "/a/directory/subdir/two.mp3": {"meta": {"recordingid": self.file2id}}}
        def metadata_side(path, *args, **kwargs):
            return ids[path]
        meta.side_effect = metadata_side

        jobs._check_existing_directories(self.collection)
        match.assert_called_once_with(self.collection.collectionid, "/a/directory/subdir")

    @mock.patch("os.listdir")
    @mock.patch("compmusic.file_metadata")
    def test_check_existing_dirs_file_changed(self, meta, listdir):
        newuuid = str(uuid.uuid4())
        def metadata_side(path, *args, **kwargs):
            if path == "/a/directory/subdir/one.mp3":
                return {"meta": {"recordingid": self.file1id}}
            elif path == "/a/directory/subdir/two.mp3":
                return {"meta": {"recordingid": newuuid}}
        listdir.return_value = ["one.mp3", "two.mp3"]
        meta.side_effect = metadata_side

        jobs._check_existing_directories(self.collection)

        cf = models.CollectionFile.objects.get(pk=self.file2.pk)
        self.assertEqual(str(cf.recordingid), newuuid)

    @mock.patch("dashboard.jobs._create_collectionfile")
    @mock.patch("os.listdir")
    @mock.patch("dashboard.jobs._get_musicbrainz_release_for_dir")
    def test_match_directory_to_release(self, get_mbrel, listdir, create_cf):
        relid = str(uuid.uuid4())
        mbrel = models.MusicbrainzRelease.objects.create(collection=self.collection, mbid=relid)

        get_mbrel.return_value = [relid]
        listdir.return_value = ["one.mp3", "two.mp3"]

        jobs._match_directory_to_release(self.collection.collectionid, "/a/directory/sub")
        cd = models.CollectionDirectory.objects.get(collection=self.collection, path="sub")

        # Check that we called create_collectionfile
        calls = [mock.call(cd, "one.mp3"), mock.call(cd, "two.mp3")]
        self.assertEqual(create_cf.mock_calls, calls)

        # Now that it's run once, we can get the CollectionDirectory and try
        # adding another file
        listdir.return_value = ["one.mp3", "two.mp3", "three.mp3"]
        create_cf.reset_mock()

        jobs._match_directory_to_release(self.collection.collectionid, "/a/directory/sub")
        calls = [mock.call(cd, "one.mp3"), mock.call(cd, "two.mp3"), mock.call(cd, "three.mp3")]
        self.assertEqual(create_cf.mock_calls, calls)


    @mock.patch("os.path.getsize")
    @mock.patch("compmusic.file_metadata")
    def test_create_collectionfile(self, meta, getsize):
        recid = str(uuid.uuid4())
        meta.return_value = {"meta": {"recordingid": recid}}
        getsize.return_value = 1000

        cd = models.CollectionDirectory.objects.create(collection=self.collection, path="sub")

        jobs._create_collectionfile(cd, "file.mp3")
        meta.assert_called_with("/a/directory/sub/file.mp3")
        getsize.assert_called_with("/a/directory/sub/file.mp3")

        self.assertEqual(models.CollectionFile.objects.get(name="file.mp3", directory=cd).filesize, 1000)

        # add again with a different size
        getsize.return_value = 2000
        jobs._create_collectionfile(cd, "file.mp3")

        self.assertEqual(models.CollectionFile.objects.get(name="file.mp3", directory=cd).filesize, 2000)

    @mock.patch("os.listdir")
    @mock.patch("compmusic.file_metadata")
    def test_get_musicbrainz_release_for_dir(self, meta, listdir):
        releaseid = str(uuid.uuid4())
        listdir.return_value = ["one.mp3", "two.mp3"]
        meta.return_value = {"meta": {"releaseid": releaseid}}

        releases = jobs._get_musicbrainz_release_for_dir("/a/dir")

        self.assertEqual(releases[0], releaseid)
        listdir.assert_called_with("/a/dir")

    def test_get_mp3_files(self):
        files = ["one.mp3", "two.wav", "three.flac", "four.mp3", "five.mp3"]
        out = jobs._get_mp3_files(files)
        self.assertEqual(out, ["one.mp3", "four.mp3", "five.mp3"])

