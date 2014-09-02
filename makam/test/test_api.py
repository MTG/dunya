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
    def test_render_release_detail(self):
        r = models.Release.objects.create(title="Rel", mbid="805a3604-92e6-482f-a0e3-6620c4523d7a")
        s = api.ReleaseDetailSerializer(r)
        self.assertEquals(["artists", "mbid", "recordings", "release_artists", "title"], sorted(s.data.keys()))

    def test_render_release_list(self):
        r = models.Release(title="Rel", mbid="805a3604-92e6-482f-a0e3-6620c4523d7a")
        s = api.ReleaseInnerSerializer(r)
        self.assertEquals(["mbid", "title"], sorted(s.data.keys()))


class RecordingTest(TestCase):
    def test_render_recording_detail(self):
        r = models.Recording.objects.create(title="recording", mbid="2a599dee-db7d-48fd-9a34-fd4e1023cfcc")
        s = api.RecordingDetailSerializer(r)
        self.assertEqual(["mbid", "performers", "releases", "title", "works"], sorted(s.data.keys()))

    def test_render_recording_list(self):
        r = models.Recording(title="recording", mbid="2a599dee-db7d-48fd-9a34-fd4e1023cfcc")
        s = api.RecordingInnerSerializer(r)
        self.assertEquals(["mbid", "title"], sorted(s.data.keys()))

class WorkTest(TestCase):
    pass

class InstrumentTest(TestCase):
    pass

class MakamTest(TestCase):
    pass

class FormTest(TestCase):
    pass

