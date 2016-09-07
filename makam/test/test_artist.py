from django.test import TestCase
import uuid

import data
from makam import models

class ArtistTest(TestCase):
    fixtures = ["makam_instrument"]

    def test_collaborating_artists(self):
        a1 = models.Artist.objects.create(name="a1")
        a2 = models.Artist.objects.create(name="a2")
        a3 = models.Artist.objects.create(name="a3")

        c1id = str(uuid.uuid4())
        c1 = data.models.Collection.objects.create(collectionid=c1id, name="collection 1", permission="U")
        c2id = str(uuid.uuid4())
        c2 = data.models.Collection.objects.create(collectionid=c2id, name="collection 2", permission="U")
        c3id = str(uuid.uuid4())
        c3 = data.models.Collection.objects.create(collectionid=c3id, name="collection 3", permission="U")
        r1 = models.Release.objects.create(collection=c1, title="r1")
        r2 = models.Release.objects.create(collection=c2, title="r2")
        r3 = models.Release.objects.create(collection=c3, title="r3")
        t1 = models.Recording.objects.create(title="t1")
        models.ReleaseRecording.objects.create(release=r1, recording=t1, track=1)
        models.InstrumentPerformance.objects.create(artist=a3, recording=t1, instrument_id=1)

        r1.artists.add(a1, a2, a3)
        r2.artists.add(a1, a2)
        r3.artists.add(a2)

        coll = a1.collaborating_artists()
        coll = sorted(coll, key=lambda a: a.name)
        self.assertEqual(2, len(coll))
        self.assertEqual([a2, a3], coll)

        coll = a2.collaborating_artists()
        self.assertEqual(2, len(coll))
        coll = sorted(coll, key=lambda a: a.name)
        self.assertEqual([a1, a3], coll)

        coll = a3.collaborating_artists()
        self.assertEqual(2, len(coll))
        coll = sorted(coll, key=lambda a: a.name)
        self.assertEqual([a1, a2], coll)

    def test_instruments(self):
        a = models.Artist.objects.create(name="artist")
        rec1 = models.Recording.objects.create(title="rec1")
        rec2 = models.Recording.objects.create(title="rec2")
        insts = models.Instrument.objects.all()
        i1 = insts[1]
        i2 = insts[2]
        models.InstrumentPerformance.objects.create(instrument=i1, artist=a, recording=rec1)
        models.InstrumentPerformance.objects.create(instrument=i2, artist=a, recording=rec1)
        models.InstrumentPerformance.objects.create(instrument=i1, artist=a, recording=rec2)
        artist_instruments = a.instruments()
        self.assertEqual(2, len(artist_instruments))
        self.assertTrue(i1 in artist_instruments)
        self.assertTrue(i2 in artist_instruments)

class ArtistReleaseListTest(TestCase):

    def setUp(self):
        c1id = str(uuid.uuid4())
        c1 = data.models.Collection.objects.create(collectionid=c1id, name="collection 1", permission="U")
        c2id = str(uuid.uuid4())
        c2 = data.models.Collection.objects.create(collectionid=c2id, name="collection 2", permission="U")
        self.rel1 = models.Release.objects.create(collection=c1, title="release1")
        self.rel2 = models.Release.objects.create(collection=c2, title="release2")
        rec1 = models.Recording.objects.create(title="rec1")
        rec2 = models.Recording.objects.create(title="rec2")
        models.ReleaseRecording.objects.create(release=self.rel1, recording=rec1, track=1)
        models.ReleaseRecording.objects.create(release=self.rel2, recording=rec2, track=1)

        self.a1 = models.Artist.objects.create(name="a1")
        self.a2 = models.Artist.objects.create(name="a2")
        self.a3 = models.Artist.objects.create(name="a3")
        self.a4 = models.Artist.objects.create(name="a4")
        self.rel1.artists.add(self.a1, self.a2)
        self.rel2.artists.add(self.a2, self.a3)

        # artist1 also performs on a rel1 recording, so rel1 won't show
        # on accomp recordings
        models.InstrumentPerformance.objects.create(recording=rec1, artist=self.a1)
        # but also performs on rel2, and will show here
        models.InstrumentPerformance.objects.create(recording=rec2, artist=self.a1)

        models.InstrumentPerformance.objects.create(recording=rec2, artist=self.a4)
        models.InstrumentPerformance.objects.create(recording=rec1, artist=self.a4)

    def test_main_releases(self):
        main_rels = self.a1.main_releases()
        self.assertEqual(1, len(main_rels))

        main_rels = self.a2.main_releases()
        self.assertEqual(2, len(main_rels))

        main_rels = self.a3.main_releases()
        self.assertEqual(1, len(main_rels))

        main_rels = self.a4.main_releases()
        self.assertEqual(0, len(main_rels))

    def test_accomp_releases(self):
        accom_rels = self.a1.accompanying_releases()
        self.assertEqual(1, len(accom_rels))
        self.assertTrue(self.rel2 in accom_rels)

        accom_rels = self.a4.accompanying_releases()
        self.assertEqual(2, len(accom_rels))
        self.assertTrue(self.rel1 in accom_rels)
        self.assertTrue(self.rel2 in accom_rels)
