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
        models.ConcertRecording.objects.create(concert=self.c1, recording=self.r1, track=1, disc=1, disctrack=1)
        # artist 1 on concert
        self.c1.artists.add(self.a1)
        # artist 2, 3 on recording rel
        models.InstrumentPerformance.objects.create(instrument=self.i, artist=self.a2, recording=self.r1)
        models.InstrumentPerformance.objects.create(instrument=self.i, artist=self.a3, recording=self.r1)

        self.c2 = models.Concert.objects.create(title="Concert2")
        self.r2 = models.Recording.objects.create(title="Recording2")
        self.r3 = models.Recording.objects.create(title="Recording3")
        models.ConcertRecording.objects.create(concert=self.c2, recording=self.r2, track=1, disc=1, disctrack=1)
        models.ConcertRecording.objects.create(concert=self.c2, recording=self.r3, track=2, disc=1, disctrack=2)
        # artist 2 on concert
        self.c2.artists.add(self.a2)
        # artist 1 & 3 on r2, but only a1 on r3
        models.InstrumentPerformance.objects.create(instrument=self.i, artist=self.a1, recording=self.r2)
        models.InstrumentPerformance.objects.create(instrument=self.i, artist=self.a3, recording=self.r2)
        models.InstrumentPerformance.objects.create(instrument=self.i, artist=self.a1, recording=self.r3)

        # A bootleg concert, with a2
        self.c3 = models.Concert.objects.create(title="Concert3", bootleg=True)
        self.r4 = models.Recording.objects.create(title="Recording4")
        models.ConcertRecording.objects.create(concert=self.c3, recording=self.r4, track=1, disc=1, disctrack=1)
        self.c3.artists.add(self.a2)


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

    def test_artist_bootleg_concerts(self):
        """ If you ask for bootlegs you get an extra concert"""
        c = self.a2.concerts(with_bootlegs=True)
        self.assertEqual(3, len(c))

    def test_artist_get_recordings(self):
        """ Recordings performed by an artist
         - explicit recording relationships
         - Also if they're a concert primary artist or have a rel
        """
        recs = self.a1.recordings()
        self.assertEqual(3, len(recs))
        recs = self.a2.recordings()
        self.assertEqual(3, len(recs))
        # A3 is not on recording3
        recs = self.a3.recordings()
        self.assertEqual(2, len(recs))

    def test_artist_bootleg_recordings(self):
        recs = self.a2.recordings(with_bootlegs=True)
        self.assertEqual(4, len(recs))

class CollaboratingArtistsTest(TestCase):
    def setUp(self):
        self.a1 = models.Artist.objects.create(name="a1")
        self.a2 = models.Artist.objects.create(name="a2")
        self.a3 = models.Artist.objects.create(name="a3")
        self.a4 = models.Artist.objects.create(name="a4")
        self.a5 = models.Artist.objects.create(name="a5")

        self.c1 = models.Concert.objects.create(title="c1")
        self.c1.artists.add(self.a1, self.a2, self.a3, self.a5)
        self.c2 = models.Concert.objects.create(title="c2")
        self.c2.artists.add(self.a1, self.a2, self.a3)
        self.c3 = models.Concert.objects.create(title="c3", bootleg=True)
        self.c3.artists.add(self.a1, self.a2, self.a3, self.a4)
        self.c4 = models.Concert.objects.create(title="c4", bootleg=True)
        self.c4.artists.add(self.a1, self.a2, self.a4)

    def test_show_bootlegs(self):
        coll = self.a1.collaborating_artists(True)
        self.assertEqual(4, len(coll))
        self.assertEqual( (self.a2, [self.c1, self.c2, self.c3, self.c4], 0), coll[0])
        self.assertEqual( (self.a3, [self.c1, self.c2, self.c3], 0), coll[1])
        self.assertEqual( (self.a4, [self.c3, self.c4], 0), coll[2])
        self.assertEqual( (self.a5, [self.c1], 0), coll[3])

    def test_dont_show_bootlegs(self):
        coll = self.a1.collaborating_artists(False)
        self.assertEqual(4, len(coll))
        self.assertEqual( (self.a2, [self.c1, self.c2], 2), coll[0])
        self.assertEqual( (self.a3, [self.c1, self.c2], 1), coll[1])
        self.assertEqual( (self.a4, [], 2), coll[2])
        self.assertEqual( (self.a5, [self.c1], 0), coll[3])
