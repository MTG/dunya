# -*- coding: utf-8 -*-
from django.test import TestCase

from dashboard import carnatic_importer
import uuid
from carnatic import models
import data

class CarnaticImporterTest(TestCase):

    def setUp(self):
        self.coll1 = data.models.Collection.objects.create(name="A collection", collectionid=uuid.uuid4())

        # Artists
        self.artist1id = str(uuid.uuid4())
        self.artist2id = str(uuid.uuid4())
        self.artist1 = models.Artist.objects.create(name="artist1", mbid=self.artist1id)
        self.artist2 = models.Artist.objects.create(name="artist2", mbid=self.artist2id)

        # Concerts
        self.concert1id = str(uuid.uuid4())
        self.concert2id = str(uuid.uuid4())
        self.concert3id = str(uuid.uuid4())
        self.concert1 = models.Concert.objects.create(title="concert1", collection=self.coll1, mbid=self.concert1id)
        self.concert2 = models.Concert.objects.create(title="concert2", collection=self.coll1, mbid=self.concert2id)
        self.concert3 = models.Concert.objects.create(title="concert3", collection=self.coll1, mbid=self.concert3id)

        self.concert1.artists.add(self.artist1)
        self.concert2.artists.add(self.artist1)
        self.concert3.artists.add(self.artist2)

        # Recordings
        self.recording1id = str(uuid.uuid4())
        self.recording2id = str(uuid.uuid4())
        self.recording3id = str(uuid.uuid4())
        self.recording1 = models.Recording.objects.create(title="recording1", mbid=self.recording1id)
        self.recording2 = models.Recording.objects.create(title="recording2", mbid=self.recording2id)
        self.recording3 = models.Recording.objects.create(title="recording3", mbid=self.recording3id)

        models.ConcertRecording.objects.create(concert=self.concert1, recording=self.recording1, track=1, disc=1, disctrack=1)
        models.ConcertRecording.objects.create(concert=self.concert2, recording=self.recording1, track=1, disc=1, disctrack=1)
        models.ConcertRecording.objects.create(concert=self.concert3, recording=self.recording2, track=1, disc=1, disctrack=1)
        models.ConcertRecording.objects.create(concert=self.concert3, recording=self.recording3, track=2, disc=1, disctrack=2)

        # works
        self.work1id = str(uuid.uuid4())
        self.work2id = str(uuid.uuid4())
        self.work1 = models.Work.objects.create(title="work1", mbid=self.work1id)
        self.work2 = models.Work.objects.create(title="work2", mbid=self.work2id)

        models.RecordingWork.objects.create(recording=self.recording1, work=self.work1, sequence=1)
        models.RecordingWork.objects.create(recording=self.recording2, work=self.work2, sequence=1)
        models.RecordingWork.objects.create(recording=self.recording3, work=self.work1, sequence=1)


    def test_remove_concert_with_shared_artist(self):

        # If you remove concert 2 and 3 then artist 1 should still be here
        # but artist 2 should be deleted
        ri = carnatic_importer.CarnaticReleaseImporter(self.coll1)
        ri.imported_releases.append(self.concert1id)
        ri.remove_nonimported_items()

        with self.assertRaises(models.Concert.DoesNotExist):
            models.Concert.objects.get(mbid=self.concert2id)
        with self.assertRaises(models.Concert.DoesNotExist):
            models.Concert.objects.get(mbid=self.concert3id)
        with self.assertRaises(models.Artist.DoesNotExist):
            models.Artist.objects.get(mbid=self.artist2id)
        self.assertIsNotNone(models.Artist.objects.get(mbid=self.artist1id))
        self.assertIsNotNone(models.Concert.objects.get(mbid=self.concert1id))

    def test_performance_artists(self):
        # If an artist performs on a track on a deleted album
        # and a non-deleted album, don't remove it
        self.artist3id = str(uuid.uuid4())
        self.artist4id = str(uuid.uuid4())
        self.artist3 = models.Artist.objects.create(name="artist3", mbid=self.artist3id)
        self.artist4 = models.Artist.objects.create(name="artist4", mbid=self.artist4id)

        inst = models.Instrument.objects.create(name="an instrument")
        models.InstrumentPerformance.objects.create(instrument=inst, artist=self.artist3, recording=self.recording1)
        models.InstrumentPerformance.objects.create(instrument=inst, artist=self.artist3, recording=self.recording2)

        models.InstrumentPerformance.objects.create(instrument=inst, artist=self.artist4, recording=self.recording2)
        models.InstrumentPerformance.objects.create(instrument=inst, artist=self.artist4, recording=self.recording3)

        ri = carnatic_importer.CarnaticReleaseImporter(self.coll1)
        ri.imported_releases.append(self.concert1id)
        ri.remove_nonimported_items()

        with self.assertRaises(models.Artist.DoesNotExist):
            models.Artist.objects.get(mbid=self.artist4id)
        self.assertIsNotNone(models.Artist.objects.get(mbid=self.artist3id))

    def test_dont_remove_dummy_artist(self):
        # some artists are flagged as 'dummy' - that is, not imported
        # by the script. We shouldn't remove them

        dummyid = str(uuid.uuid4())
        a = models.Artist.objects.create(name="dummyartist", mbid=dummyid, dummy=True)
        ri = carnatic_importer.CarnaticReleaseImporter(self.coll1)
        ri.imported_releases.append(self.concert1id)
        ri.remove_nonimported_items()
        self.assertIsNotNone(models.Artist.objects.get(mbid=dummyid))

    def test_shared_recording(self):
        # If recording 1 is part of concert 1 and 2, and
        # recording 2 is part of concert 3 you delete concert 2 and 3
        # then recording 1 stays and recording 2 gets deleted
        ri = carnatic_importer.CarnaticReleaseImporter(self.coll1)
        ri.imported_releases.append(self.concert1id)
        ri.remove_nonimported_items()

        with self.assertRaises(models.Recording.DoesNotExist):
            models.Recording.objects.get(mbid=self.recording2id)
        self.assertIsNotNone(models.Recording.objects.get(mbid=self.recording1.mbid))

    def test_shared_work(self):
        # If a work is part of a non-deleted recording and a deleted one,
        # don't delete the work
        ri = carnatic_importer.CarnaticReleaseImporter(self.coll1)
        ri.imported_releases.append(self.concert1id)
        ri.remove_nonimported_items()

        with self.assertRaises(models.Recording.DoesNotExist):
            models.Recording.objects.get(mbid=self.recording3id)
        with self.assertRaises(models.Work.DoesNotExist):
            models.Work.objects.get(mbid=self.work2id)
        self.assertIsNotNone(models.Recording.objects.get(mbid=self.recording1id))
        self.assertIsNotNone(models.Work.objects.get(mbid=self.work1id))

    def test_composers(self):
        self.composer1id = str(uuid.uuid4())
        self.composer2id = str(uuid.uuid4())
        self.composer3id = str(uuid.uuid4())
        self.composer4id = str(uuid.uuid4())

        self.composer1 = models.Composer.objects.create(name="composer1", mbid=self.composer1id)
        self.composer2 = models.Composer.objects.create(name="composer2", mbid=self.composer2id)
        self.composer3 = models.Composer.objects.create(name="composer3", mbid=self.composer3id)
        self.composer4 = models.Composer.objects.create(name="composer4", mbid=self.composer4id)

        self.work1.composers.add(self.composer1)
        self.work2.composers.add(self.composer1)
        self.work2.composers.add(self.composer2)
        self.work2.lyricists.add(self.composer3)
        self.work1.lyricists.add(self.composer4)

        ri = carnatic_importer.CarnaticReleaseImporter(self.coll1)
        ri.imported_releases.append(self.concert1id)
        ri.remove_nonimported_items()

        with self.assertRaises(models.Composer.DoesNotExist):
            models.Composer.objects.get(mbid=self.composer2id)
        with self.assertRaises(models.Composer.DoesNotExist):
            models.Composer.objects.get(mbid=self.composer3id)
        self.assertIsNotNone(models.Composer.objects.get(mbid=self.composer1id))
        self.assertIsNotNone(models.Composer.objects.get(mbid=self.composer4id))
