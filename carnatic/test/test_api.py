from django.test import TestCase

from carnatic import models
from carnatic import api

class ArtistTest(TestCase):
    def test_render_artist_inner(self):
        a = models.Artist(name="Foo", mbid="a484bcbc-c0d9-468a-952c-9938d5811f85")
        s = api.ArtistInnerSerializer(a)
        expected = {"name": "Foo", "mbid": "a484bcbc-c0d9-468a-952c-9938d5811f85"}
        self.assertEquals(expected, s.data)

    def test_render_artist_detail(self):
        pass

class ComposerTest(TestCase):
    pass

class RecordingTest(TestCase):
    pass

class WorkTest(TestCase):
    pass

class RaagaTest(TestCase):
    pass

class TaalaTest(TestCase):
    pass

class ConcertTest(TestCase):
    pass

class InstrumentTest(TestCase):
    pass
