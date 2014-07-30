from django.test import TestCase

from carnatic import models

class ArtistCountTest(TestCase):
    """ Test the artists for a recording, or a concert,
        or the concerts or recordings for an artist using
        all available relationships
    """

    def setUp(self):
        self.i = models.Instrument.objects.create(name="Violin")
        self.a1 = models.Artist.objects.create(name="Artist1", main_instrument=self.i)
        self.a2 = models.Artist.objects.create(name="Artist2", main_instrument=self.i)
        self.a3 = models.Artist.objects.create(name="Artist3", main_instrument=self.i)

        self.c1 = models.Concert.objects.create(title="Concert1")
        self.r1 = models.Recording.objects.create(title="Recording1")
        models.ConcertRecording.objects.create(concert=self.c1, recording=self.r1, track=1)
        # artist 1 on concert
        self.c1.artists.add(self.a1)
        # artist 2, 3 on recording rel
        models.InstrumentPerformance.objects.create(instrument=self.i, performer=self.a2, recording=self.r1)
        models.InstrumentPerformance.objects.create(instrument=self.i, performer=self.a3, recording=self.r1)

        self.c2 = models.Concert.objects.create(title="Concert2")
        self.r2 = models.Recording.objects.create(title="Recording2")
        self.r3 = models.Recording.objects.create(title="Recording3")
        models.ConcertRecording.objects.create(concert=self.c2, recording=self.r2, track=1)
        models.ConcertRecording.objects.create(concert=self.c2, recording=self.r3, track=2)
        # artist 2 on concert
        self.c2.artists.add(self.a2)
        # artist 1 & 3 on r2, but only a1 on r3
        models.InstrumentPerformance.objects.create(instrument=self.i, performer=self.a1, recording=self.r2)
        models.InstrumentPerformance.objects.create(instrument=self.i, performer=self.a3, recording=self.r2)
        models.InstrumentPerformance.objects.create(instrument=self.i, performer=self.a1, recording=self.r3)

    def test_recording_get_artists(self):
        """ The artists that performed on a recording
            - Artists with performance relationship on the recording
            - Artists with perf rel on the concert this rec is part of
            - Primary artists of the concert
        """
        artists = self.r1.all_artists()
        self.assertEqual(3, len(artists))

        artists = self.r2.all_artists()
        self.assertEqual(3, len(artists))

        artists = self.r3.all_artists()
        self.assertEqual(2, len(artists))

    def test_concert_get_artists(self):
        """ Artists who performed on a concert
         - if they are a primary artist
         - If they're a relationship on the concert
         - If they're a relationship on a track
        """
        artists = self.c1.performers()
        self.assertEqual(3, len(artists))

        artists = self.c2.performers()
        self.assertEqual(3, len(artists))

    def test_artist_get_concerts(self):
        """ Concerts performed by an artist """
        c = self.a1.concerts()
        self.assertEqual(2, len(c))
        c = self.a2.concerts()
        self.assertEqual(2, len(c))
        c = self.a3.concerts()
        self.assertEqual(2, len(c))

        concert = models.Concert.objects.create(title="Other concert")
        concert.artists.add(self.a3)
        c = self.a3.concerts()
        self.assertEqual(3, len(c))

    def test_artist_group_get_concerts(self):
        """ If you're in a group, you performed in that group's concerts """
        grp = models.Artist.objects.create(name="Group")
        art = models.Artist.objects.create(name="Artist")
        grp.group_members.add(art)
        concert = models.Concert.objects.create(title="Other concert")
        c = art.concerts()
        self.assertEqual(0, len(c))
        concert.artists.add(grp)
        c = art.concerts()
        self.assertEqual(1, len(c))

    def test_artist_get_recordings(self):
        """ Recordings performed by an artist
         - explicit recording relationships
         - Also if they're a concert primary artist or have a rel
        """
        c = self.a1.recordings()
        self.assertEqual(3, len(c))
        c = self.a2.recordings()
        self.assertEqual(3, len(c))
        # A3 is not on recording3
        c = self.a3.recordings()
        self.assertEqual(2, len(c))
