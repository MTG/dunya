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
    def test_render_composer_detail(self):
        c = models.Composer.objects.create(name="Composer", mbid="392fa7ab-f87d-4a07-9c83-bd23130e711b")
        s = api.ComposerDetailSerializer(c)
        self.assertEqual(["lyric_works", "mbid", "name", "works"], sorted(s.data.keys()))

    def test_render_composer_list(self):
        c = models.Composer.objects.create(name="Composer", mbid="392fa7ab-f87d-4a07-9c83-bd23130e711b")
        s = api.ComposerInnerSerializer(c)
        expected = {"name": "Composer", "mbid": "392fa7ab-f87d-4a07-9c83-bd23130e711b"}
        self.assertEquals(expected, s.data)

class ReleaseTest(TestCase):
    def test_render_release_detail(self):
        r = models.Release.objects.create(title="Rel", mbid="805a3604-92e6-482f-a0e3-6620c4523d7a")
        s = api.ReleaseDetailSerializer(r)
        self.assertEquals(["artists", "mbid", "recordings", "release_artists", "title", "year"], sorted(s.data.keys()))

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
    def test_render_work_detail(self):
        w = models.Work.objects.create(title="work", mbid="5f41f3ed-6c48-403f-ba6c-3e810b58295c")
        s = api.WorkDetailSerializer(w)
        fields = ['mbid', 'title', 'composers', 'lyricists', 'makams', 'forms', 'usuls', 'recordings']
        self.assertEquals(sorted(fields), sorted(s.data.keys()))


    def test_render_work_list(self):
        w = models.Work(title="work", mbid="5f41f3ed-6c48-403f-ba6c-3e810b58295c")
        s = api.WorkInnerSerializer(w)
        self.assertEquals(["mbid", "title"], sorted(s.data.keys()))

class InstrumentTest(TestCase):
    def setUp(self):
        self.i1 = models.Instrument.objects.create(name="inst1")
        self.rec1 = models.Recording.objects.create(title="rec1")
        self.a1 = models.Artist.objects.create(name="a1")
        models.InstrumentPerformance.objects.create(recording=self.rec1, artist=self.a1, instrument=self.i1)

    def test_render_instrument_detail(self):
        s = api.InstrumentDetailSerializer(self.i1)
        self.assertEquals(["artists", "id", "name"], sorted(s.data.keys()))
        self.assertEquals(1, len(s.data["artists"]))

    def test_render_instrument_list(self):
        s = api.InstrumentInnerSerializer(self.i1)
        self.assertEquals(["id", "name"], sorted(s.data.keys()))

class MakamTest(TestCase):
    def test_render_makam_detail(self):
        m = models.Makam.objects.create(name="makam")
        s = api.MakamDetailSerializer(m)
        self.assertEquals(["gazels", "id", "name", "taksims", "works"], sorted(s.data.keys()))

    def test_render_makam_list(self):
        m = models.Makam.objects.create(name="makam")
        s = api.MakamInnerSerializer(m)
        self.assertEquals(["id", "name"], sorted(s.data.keys()))

class FormTest(TestCase):
    def test_render_form_detail(self):
        f = models.Form.objects.create(name="form")
        s = api.FormDetailSerializer(f)
        self.assertEquals(["id", "name", "works"], sorted(s.data.keys()))

    def test_render_form_list(self):
        f = models.Form.objects.create(name="form")
        s = api.FormInnerSerializer(f)
        self.assertEquals(["id", "name"], sorted(s.data.keys()))

class UsulTest(TestCase):
    def test_render_usul_detail(self):
        u = models.Usul.objects.create(name="usul")
        s = api.UsulDetailSerializer(u)
        self.assertEquals(["gazels", "id", "name", "taksims", "works"], sorted(s.data.keys()))

    def test_render_usul_list(self):
        u = models.Usul.objects.create(name="usul")
        s = api.UsulInnerSerializer(u)
        self.assertEquals(["id", "name"], sorted(s.data.keys()))

