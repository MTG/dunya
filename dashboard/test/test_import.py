import uuid
from unittest import mock

from django.test import TestCase

from dashboard import jobs, models


class CollectionTest(TestCase):
    def setUp(self):
        u = str(uuid.uuid4())
        self.collection = models.Collection.objects.create(
            collectionid=u, name="Test collection", root_directory="/a/directory"
        )
        self.directory = models.CollectionDirectory.objects.create(collection=self.collection, path="subdir")

        self.file1id = str(uuid.uuid4())
        self.file1 = models.CollectionFile.objects.create(
            name="one.mp3", directory=self.directory, recordingid=self.file1id
        )
        self.file2id = str(uuid.uuid4())
        self.file2 = models.CollectionFile.objects.create(
            name="two.mp3", directory=self.directory, recordingid=self.file2id
        )

    @mock.patch("compmusic.file_metadata")
    @mock.patch("os.listdir")
    @mock.patch("dashboard.jobs._get_mp3_files")
    def test_check_existing_dirs_file_removed(self, get_mp3_files, listdir, meta):
        listdir.return_value = ["one.mp3"]
        get_mp3_files.return_value = ["one.mp3"]
        meta.return_value = {"meta": {"recordingid": self.file1id}}

        self.assertEqual(2, len(self.directory.collectionfile_set.all()))
        jobs._check_existing_directories(self.collection)

        self.assertEqual(1, len(self.directory.collectionfile_set.all()))

    @mock.patch("compmusic.file_metadata")
    @mock.patch("dashboard.jobs._match_directory_to_release")
    @mock.patch("os.listdir")
    @mock.patch("dashboard.jobs._get_mp3_files")
    def test_check_existing_dirs_file_added(self, get_mp3_files, listdir, match, meta):
        files = ["one.mp3", "two.mp3", "three.mp3"]
        get_mp3_files.return_value = files
        listdir.return_value = files

        ids = {
            "/a/directory/audio/subdir/one.mp3": {"meta": {"recordingid": self.file1id}},
            "/a/directory/audio/subdir/two.mp3": {"meta": {"recordingid": self.file2id}},
        }

        def metadata_side(path, *args, **kwargs):
            return ids[path]

        meta.side_effect = metadata_side

        jobs._check_existing_directories(self.collection)
        match.assert_called_once_with(self.collection.collectionid, "/a/directory/audio/subdir")

    @mock.patch("os.listdir")
    @mock.patch("compmusic.file_metadata")
    @mock.patch("dashboard.jobs._get_mp3_files")
    def test_check_existing_dirs_file_changed(self, get_mp3_files, meta, listdir):
        newuuid = str(uuid.uuid4())

        def metadata_side(path, *args, **kwargs):
            if path == "/a/directory/audio/subdir/one.mp3":
                return {"meta": {"recordingid": self.file1id}}
            elif path == "/a/directory/audio/subdir/two.mp3":
                return {"meta": {"recordingid": newuuid}}

        files = ["one.mp3", "two.mp3"]
        listdir.return_value = files
        get_mp3_files.return_value = files
        meta.side_effect = metadata_side

        jobs._check_existing_directories(self.collection)

        cf = models.CollectionFile.objects.get(pk=self.file2.pk)
        self.assertEqual(str(cf.recordingid), newuuid)

    @mock.patch("dashboard.jobs._create_collectionfile")
    @mock.patch("os.listdir")
    @mock.patch("dashboard.jobs._get_musicbrainz_release_for_dir")
    @mock.patch("dashboard.jobs._get_mp3_files")
    def test_match_directory_to_release(self, get_mp3_files, get_mbrel, listdir, create_cf):
        relid = str(uuid.uuid4())
        models.MusicbrainzRelease.objects.create(collection=self.collection, mbid=relid)

        get_mbrel.return_value = [relid]
        files = ["one.mp3", "two.mp3"]
        listdir.return_value = files
        get_mp3_files.return_value = files

        jobs._match_directory_to_release(self.collection.collectionid, "/a/directory/audio/sub")
        cd = models.CollectionDirectory.objects.get(collection=self.collection, path="sub")

        # Check that we called create_collectionfile
        calls = [mock.call(cd, "one.mp3"), mock.call(cd, "two.mp3")]
        self.assertEqual(create_cf.mock_calls, calls)

        # Now that it's run once, we can get the CollectionDirectory and try
        # adding another file
        files = ["one.mp3", "two.mp3", "three.mp3"]
        listdir.return_value = files
        get_mp3_files.return_value = files
        create_cf.reset_mock()

        jobs._match_directory_to_release(self.collection.collectionid, "/a/directory/audio/sub")
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
        meta.assert_called_with("/a/directory/audio/sub/file.mp3")
        getsize.assert_called_with("/a/directory/audio/sub/file.mp3")

        self.assertEqual(models.CollectionFile.objects.get(name="file.mp3", directory=cd).filesize, 1000)

        # add again with a different size
        getsize.return_value = 2000
        jobs._create_collectionfile(cd, "file.mp3")

        self.assertEqual(models.CollectionFile.objects.get(name="file.mp3", directory=cd).filesize, 2000)

    @mock.patch("os.listdir")
    @mock.patch("compmusic.file_metadata")
    @mock.patch("dashboard.jobs._get_mp3_files")
    def test_get_musicbrainz_release_for_dir(self, get_mp3_files, meta, listdir):
        files = ["one.mp3", "two.mp3"]
        releaseid = str(uuid.uuid4())
        listdir.return_value = files
        get_mp3_files.return_value = files
        meta.return_value = {"meta": {"releaseid": releaseid}}

        releases = jobs._get_musicbrainz_release_for_dir("/a/dir")

        self.assertEqual(releases[0], releaseid)
        listdir.assert_called_with("/a/dir")
        get_mp3_files.assert_called_with("/a/dir", files)

    @mock.patch("os.path.isfile")
    @mock.patch("magic.from_file")
    def test_get_mp3_files(self, from_file, is_file):
        is_file.return_value = True
        from_file.side_effect = ["audio/mpeg", "audio/wav", "audio/flac", "audio/mpeg", "audio/mpeg"]

        files = ["one.mp3", "two.wav", "three.flac", "four.mp3", "five.mp3"]
        dirname = "/path"
        out = jobs._get_mp3_files(dirname, files)
        self.assertEqual(out, ["one.mp3", "four.mp3", "five.mp3"])
