from django.test import TestCase

from makam import models

class ReleaseTest(TestCase):
    fixtures = ["makam_instrument", ]

    def setUp(self):
        self.release = models.Release.objects.create(title="rel")
        self.recording1 = models.Recording.objects.create(title="rec")
        self.recording2 = models.Recording.objects.create(title="rec")
        models.ReleaseRecording.objects.create(release=self.release, recording=self.recording1, track=1)
        models.ReleaseRecording.objects.create(release=self.release, recording=self.recording2, track=2)

        self.a1 = models.Artist.objects.create(name="a1")
        self.a2 = models.Artist.objects.create(name="a2")
        self.a3 = models.Artist.objects.create(name="a3")
        self.a4 = models.Artist.objects.create(name="a4")

        self.i1 = models.Instrument.objects.all()[0]
        self.i2 = models.Instrument.objects.all()[1]
        self.i3 = models.Instrument.objects.all()[2]

        self.release.artists.add(self.a1)
        models.InstrumentPerformance.objects.create(recording=self.recording1, artist=self.a1, instrument=self.i1)
        models.InstrumentPerformance.objects.create(recording=self.recording1, artist=self.a2, instrument=self.i2)
        models.InstrumentPerformance.objects.create(recording=self.recording2, artist=self.a2, instrument=self.i3)
        models.InstrumentPerformance.objects.create(recording=self.recording2, artist=self.a3, instrument=self.i2)
        models.InstrumentPerformance.objects.create(recording=self.recording2, artist=self.a3, instrument=self.i1)


    def test_get_performers(self):
        perfs = self.release.performers()
        self.assertEqual(3, len(perfs))
        perfs = sorted(perfs, key=lambda p: p.name)
        print perfs
        self.assertEqual(self.a1, perfs[0])
        self.assertEqual(self.a2, perfs[1])
        self.assertEqual(self.a3, perfs[2])

    def test_get_instruments_for_artist(self):
        ins = self.release.instruments_for_artist(self.a2)
        self.assertEqual(2, len(ins))

    def test_ordered_recordings(self):
        """ If recordings are added out of order (e,g, 1, 3, 2) then when getting
        the list of recordings of a release they will be returned in correct order """
        rel = models.Release.objects.create(title="release")
        rec2 = models.Recording.objects.create(title="recording 2")
        rec1 = models.Recording.objects.create(title="recording 1")
        models.ReleaseRecording.objects.create(release=rel, recording=rec2, track=2)
        models.ReleaseRecording.objects.create(release=rel, recording=rec1, track=1)

        tl = rel.tracklist()
        self.assertEqual(rec1, tl[0])
        self.assertEqual(rec2, tl[1])

