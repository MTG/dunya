from django.test import TestCase

from carnatic import models
import data

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
        
        self.col1 = data.models.Collection.objects.create(name="collection 1", mbid='f44f4f73', permission="U") 
        self.c1 = models.Concert.objects.create(collection=self.col1, title="Concert1")
        self.r1 = models.Recording.objects.create(title="Recording1")
        models.ConcertRecording.objects.create(concert=self.c1, recording=self.r1, track=1, disc=1, disctrack=1)
        # artist 1 on concert
        self.c1.artists.add(self.a1)
        # artist 2, 3 on recording rel
        models.InstrumentPerformance.objects.create(instrument=self.i, artist=self.a2, recording=self.r1)
        models.InstrumentPerformance.objects.create(instrument=self.i, artist=self.a3, recording=self.r1)

        self.col2 = data.models.Collection.objects.create(name="collection 2", mbid='f55f5f73', permission="U") 
        self.c2 = models.Concert.objects.create(collection=self.col2, title="Concert2")
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

        # A concert from restricted collection, with a2
        self.col3 = data.models.Collection.objects.create(name="collection 3", mbid='f66f6f73', permission="S") 
        self.c3 = models.Concert.objects.create(collection=self.col3, title="Concert3")
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

        col = data.models.Collection.objects.create(name="collection 4", mbid='f77f7f73', permission="U") 
        concert = models.Concert.objects.create(collection=col, title="Other concert")
        concert.artists.add(self.a3)
        c = self.a3.concerts()
        self.assertEqual(3, len(c))

    def test_artist_group_get_concerts(self):
        """ If you're in a group, you performed in that group's concerts """
        grp = models.Artist.objects.create(name="Group")
        art = models.Artist.objects.create(name="Artist")
        grp.group_members.add(art)
        col = data.models.Collection.objects.create(name="collection 4", mbid='f77f7f73', permission="U") 
        concert = models.Concert.objects.create(collection=col, title="Other concert")
        c = art.concerts()
        self.assertEqual(0, len(c))
        concert.artists.add(grp)
        c = art.concerts()
        self.assertEqual(1, len(c))

    def test_artist_restr_collection_concerts(self):
        """ If you ask for a restricted collection you get an extra concert"""
        c = self.a2.concerts(collection_ids='f44f4f73, f55f5f73, f66f6f73', permission=['U', 'R', 'S'])
        self.assertEqual(3, len(c))

    def test_artist_get_recordings(self):
        """ Recordings performed by an artist
         - explicit recording relationships
         - Also if they're a concert primary artist or have a rel
        """
        recs = self.a1.recordings(collection_ids='f44f4f73, f55f5f73, f66f6f73', permission=['U'])
        self.assertEqual(3, len(recs))
        recs = self.a2.recordings(collection_ids='f44f4f73, f55f5f73, f66f6f73', permission=['U'])
        self.assertEqual(3, len(recs))
        # A3 is not on recording3
        recs = self.a3.recordings(collection_ids='f44f4f73, f55f5f73, f66f6f73', permission=['U'])
        self.assertEqual(2, len(recs))

    def test_artist_collection_recordings(self):
        recs = self.a2.recordings(collection_ids='f44f4f73, f55f5f73, f66f6f73', permission=['U', 'R', 'S'])
        self.assertEqual(4, len(recs))

class CollaboratingArtistsTest(TestCase):
    def setUp(self):
        self.a1 = models.Artist.objects.create(name="a1")
        self.a2 = models.Artist.objects.create(name="a2")
        self.a3 = models.Artist.objects.create(name="a3")
        self.a4 = models.Artist.objects.create(name="a4")
        self.a5 = models.Artist.objects.create(name="a5")

        self.col1 = data.models.Collection.objects.create(name="collection 1", mbid='f11f1f73', permission="U") 
        self.c1 = models.Concert.objects.create(collection=self.col1, title="c1")
        self.c1.artists.add(self.a1, self.a2, self.a3, self.a5)
        self.col2 = data.models.Collection.objects.create(name="collection 2", mbid='f22f2f73', permission="U") 
        self.c2 = models.Concert.objects.create(collection=self.col2, title="c2")
        self.c2.artists.add(self.a1, self.a2, self.a3)
        self.col3 = data.models.Collection.objects.create(name="collection 3", mbid='f33f3f73', permission="S") 
        self.c3 = models.Concert.objects.create(collection=self.col3, title="c3")
        self.c3.artists.add(self.a1, self.a2, self.a3, self.a4)
        self.col4 = data.models.Collection.objects.create(name="collection 4", mbid='f44f4f73', permission="S") 
        self.c4 = models.Concert.objects.create(collection=self.col4, title="c4")
        self.c4.artists.add(self.a1, self.a2, self.a4)

    def test_show_collectionss(self):
        coll = self.a1.collaborating_artists(collection_ids='f11f1f73, f22f2f73, f33f3f73, f44f4f73', permission=['U','R','S'])
        self.assertEqual(4, len(coll))
        self.assertEqual( (self.a2, [self.c1, self.c2, self.c3, self.c4], 0), coll[0])
        self.assertEqual( (self.a3, [self.c1, self.c2, self.c3], 0), coll[1])
        self.assertEqual( (self.a4, [self.c3, self.c4], 0), coll[2])
        self.assertEqual( (self.a5, [self.c1], 0), coll[3])

    def test_dont_show_collections(self):
        coll = self.a1.collaborating_artists(collection_ids='f11f1f73, f22f2f73, f33f3f73, f44f4f73', permission=['U'])
        self.assertEqual(4, len(coll))
        self.assertEqual( (self.a2, [self.c1, self.c2], 2), coll[0])
        self.assertEqual( (self.a3, [self.c1, self.c2], 1), coll[1])
        self.assertEqual( (self.a4, [], 2), coll[2])
        self.assertEqual( (self.a5, [self.c1], 0), coll[3])
