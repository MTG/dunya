from django.test import TestCase

from makam import models

class ArtistTest(TestCase):
    def test_collaborating_artists(self):
        a1 = models.Artist.objects.create(name="a1")
        a2 = models.Artist.objects.create(name="a2")
        a3 = models.Artist.objects.create(name="a3")

        r1 = models.Release.objects.create(title="r1")
        r2 = models.Release.objects.create(title="r2")
        r3 = models.Release.objects.create(title="r3")
        t1 = models.Recording.objects.create(title="t1")
        models.ReleaseRecording.objects.create(release=r1, recording=t1, track=1)
        models.InstrumentPerformance.objects.create(artist=a3, recording=t1, instrument_id=1)

        r1.artists.add(a1, a2, a3)
        r2.artists.add(a1, a2)
        r3.artists.add(a2)

        coll = a1.collaborating_artists()
        self.assertEqual(2, len(coll))
        self.assertEqual([a2, a3], coll)

        coll = a2.collaborating_artists()
        self.assertEqual(2, len(coll))
        self.assertEqual([a1, a3], coll)

        coll = a3.collaborating_artists()
        self.assertEqual(2, len(coll))
        self.assertEqual([a1, a2], coll)
