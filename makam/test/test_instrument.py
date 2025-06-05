from django.test import TestCase

from makam import models


class InstrumentTest(TestCase):
    def test_artists(self):
        i1 = models.Instrument.objects.create(name="inst1")
        i2 = models.Instrument.objects.create(name="inst2")

        rec1 = models.Recording.objects.create(title="rec1")
        rec2 = models.Recording.objects.create(title="rec2")
        models.Recording.objects.create(title="rec3")

        a1 = models.Artist.objects.create(name="a1")
        a2 = models.Artist.objects.create(name="a2")

        models.InstrumentPerformance.objects.create(recording=rec1, artist=a1, instrument=i1)
        models.InstrumentPerformance.objects.create(recording=rec1, artist=a1, instrument=i2)
        models.InstrumentPerformance.objects.create(recording=rec2, artist=a2, instrument=i1)
        models.InstrumentPerformance.objects.create(recording=rec2, artist=a1, instrument=i1)

        artists = i1.artists()
        self.assertEqual(2, len(artists))
        artists = i2.artists()
        self.assertEqual(1, len(artists))
        self.assertTrue(a1 in artists)
