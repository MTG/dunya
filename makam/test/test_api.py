from django.test import TestCase

from makam import models
from makam import api

class ArtistTest(TestCase):
    def test_render_artist_detail(self):
        a = models.Artist.objects.create(name="Artist", mbid="a484bcbc-c0d9-468a-952c-9938d5811f85")
        s = api.ArtistDetailSerializer(a)
        self.assertEqual(["instruments", "mbid", "name", "releases"], sorted(s.data.keys()))

    def test_render_artist_list(self):
        a = models.Artist.objects.create(name="Artist", mbid="a484bcbc-c0d9-468a-952c-9938d5811f85")
        s = api.ArtistInnerSerializer(a)
        expected = {"name": "Artist", "mbid": "a484bcbc-c0d9-468a-952c-9938d5811f85"}
        self.assertEquals(expected, s.data)

class ComposerTest(TestCase):
    pass

class ReleaseTest(TestCase):
    pass

class RecordingTest(TestCase):
    pass

class WorkTest(TestCase):
    pass

class InstrumentTest(TestCase):
    pass

class MakamTest(TestCase):
    pass

class FormTest(TestCase):
    pass

