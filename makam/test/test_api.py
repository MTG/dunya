from django.test import TestCase
from django.contrib import auth
from rest_framework.test import APIClient

import data
from makam import models
from makam import api

class ApiTestCase(TestCase):
    def setUp(self):
        self.col = data.models.Collection.objects.create(mbid="f33f3f73", name="collection 1", permission="U") 
        self.r = models.Release.objects.create(collection=self.col, title="Rel", mbid="805a3604-92e6-482f-a0e3-6620c4523d7a")

        self.rec = models.Recording.objects.create(title="recording", mbid="2a599dee-db7d-48fd-9a34-fd4e1023cfcc")
        models.ReleaseRecording.objects.create(release=self.r, recording=self.rec, track=1)

        self.staffuser = auth.models.User.objects.create_user("staffuser")
        self.staffuser.is_staff = True
        self.staffuser.save()

        self.apiclient = APIClient()
        self.apiclient.force_authenticate(user=self.staffuser)

class ArtistTest(ApiTestCase):
    def setUp(self):
        super(ArtistTest, self).setUp()
        self.a = models.Artist.objects.create(name="Artist", mbid="a484bcbc-c0d9-468a-952c-9938d5811f85")

    def test_render_artist_detail(self):
        response = self.apiclient.get("/api/makam/artist/a484bcbc-c0d9-468a-952c-9938d5811f85")
        data = response.data
         
        keys = sorted(data.keys())
        self.assertEqual(["instruments", "mbid", "name", "releases"], keys)

    def test_render_artist_list(self):
        s = api.ArtistInnerSerializer(self.a)
        expected = {"name": "Artist", "mbid": "a484bcbc-c0d9-468a-952c-9938d5811f85"}
        self.assertEquals(expected, s.data)

    def test_artist_detail_url(self):
        resp = self.apiclient.get("/api/makam/artist/a484bcbc-c0d9-468a-952c-9938d5811f85")
        self.assertEqual(200, resp.status_code)

    def test_artist_list_url(self):
        resp = self.apiclient.get("/api/makam/artist")
        self.assertEqual(200, resp.status_code)
        self.assertEqual(1, len(resp.data["results"]))

class ComposerTest(ApiTestCase):
    def setUp(self):
        super(ComposerTest, self).setUp()
        self.c = models.Composer.objects.create(name="Composer", mbid="392fa7ab-f87d-4a07-9c83-bd23130e711b")

    def test_render_composer_detail(self):
        s = api.ComposerDetailSerializer(self.c)
        self.assertEqual(["lyric_works", "mbid", "name", "works"], sorted(s.data.keys()))

    def test_render_composer_list(self):
        s = api.ComposerInnerSerializer(self.c)
        expected = {"name": "Composer", "mbid": "392fa7ab-f87d-4a07-9c83-bd23130e711b"}
        self.assertEquals(expected, s.data)

    def test_composer_detail_url(self):
        resp = self.apiclient.get("/api/makam/composer/392fa7ab-f87d-4a07-9c83-bd23130e711b")
        self.assertEqual(200, resp.status_code)

    def test_composer_list_url(self):
        resp = self.apiclient.get("/api/makam/composer")
        self.assertEqual(200, resp.status_code)
        self.assertEqual(1, len(resp.data["results"]))

class ReleaseTest(ApiTestCase):

    def test_render_release_detail(self):
        s = api.ReleaseDetailSerializer(self.r)
        self.assertEquals(["artists", "image", "mbid", "recordings", "release_artists", "title", "year"], sorted(s.data.keys()))

    def test_render_release_list(self):
        s = api.ReleaseInnerSerializer(self.r)
        self.assertEquals(["mbid", "title"], sorted(s.data.keys()))

    def test_release_detail_url(self):
        resp = self.apiclient.get("/api/makam/release/805a3604-92e6-482f-a0e3-6620c4523d7a")
        self.assertEqual(200, resp.status_code)

    def test_release_list_url(self):
        resp = self.apiclient.get("/api/makam/release")
        self.assertEqual(200, resp.status_code)
        self.assertEqual(1, len(resp.data["results"]))


class RecordingTest(ApiTestCase):
    def setUp(self):
        super(RecordingTest, self).setUp()
        pass

    def test_render_recording_detail(self):
        resp = self.apiclient.get("/api/makam/recording/2a599dee-db7d-48fd-9a34-fd4e1023cfcc")
        self.assertEqual(["mbid", "performers", "releases", "title", "works"], sorted(resp.data.keys()))

    def test_render_recording_list(self):
        s = api.RecordingInnerSerializer(self.r)
        self.assertEquals(["mbid", "title"], sorted(s.data.keys()))

    def test_recording_detail_url(self):
        resp = self.apiclient.get("/api/makam/recording/2a599dee-db7d-48fd-9a34-fd4e1023cfcc")
        self.assertEqual(200, resp.status_code)

    def test_recording_list_url(self):
        resp = self.apiclient.get("/api/makam/recording")
        self.assertEqual(200, resp.status_code)
        self.assertEqual(1, len(resp.data["results"]))


class WorkTest(ApiTestCase):
    def setUp(self):
        super(WorkTest, self).setUp()
        self.w = models.Work.objects.create(title="work", mbid="5f41f3ed-6c48-403f-ba6c-3e810b58295c")

    def test_render_work_detail(self):
        resp = self.apiclient.get("/api/makam/work/5f41f3ed-6c48-403f-ba6c-3e810b58295c")
        fields = ['mbid', 'title', 'composers', 'lyricists', 'makams', 'forms', 'usuls', 'recordings']
        self.assertEquals(sorted(fields), sorted(resp.data.keys()))

    def test_render_work_list(self):
        s = api.WorkInnerSerializer(self.w)
        self.assertEquals(["mbid", "title"], sorted(s.data.keys()))

    def test_recording_detail_url(self):
        resp = self.apiclient.get("/api/makam/work/5f41f3ed-6c48-403f-ba6c-3e810b58295c")
        self.assertEqual(200, resp.status_code)

    def test_recording_list_url(self):
        resp = self.apiclient.get("/api/makam/work")
        self.assertEqual(200, resp.status_code)
        self.assertEqual(1, len(resp.data["results"]))


class InstrumentTest(ApiTestCase):
    def setUp(self):
        super(InstrumentTest, self).setUp()
        self.i1 = models.Instrument.objects.create(pk=3, name="inst1")
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

    def test_instrument_detail_url(self):
        resp = self.apiclient.get("/api/makam/instrument/3")
        self.assertEqual(200, resp.status_code)

    def test_instrument_list_url(self):
        resp = self.apiclient.get("/api/makam/instrument")
        self.assertEqual(200, resp.status_code)
        self.assertEqual(1, len(resp.data["results"]))


class MakamTest(ApiTestCase):
    def setUp(self):
        super(MakamTest, self).setUp()
        self.m = models.Makam.objects.create(name="makam", uuid="9c9b77cc-e357-402f-9278-2c5ed49e06b7")

    def test_render_makam_detail(self):
        s = api.MakamDetailSerializer(self.m)
        self.assertEquals(["gazels", "id", "name", "taksims", "works"], sorted(s.data.keys()))

    def test_render_makam_list(self):
        s = api.MakamInnerSerializer(self.m)
        self.assertEquals(["id", "name"], sorted(s.data.keys()))

    def test_instrument_detail_url(self):
        resp = self.apiclient.get("/api/makam/makam/9c9b77cc-e357-402f-9278-2c5ed49e06b7")
        self.assertEqual(200, resp.status_code)

    def test_instrument_list_url(self):
        resp = self.apiclient.get("/api/makam/makam")
        self.assertEqual(200, resp.status_code)
        self.assertEqual(1, len(resp.data["results"]))

class FormTest(ApiTestCase):
    def setUp(self):
        super(FormTest, self).setUp()
        self.f = models.Form.objects.create(name="form", uuid="1494b665-8b67-430f-b6e6-efdcd42ddd3f")

    def test_render_form_detail(self):
        s = api.FormDetailSerializer(self.f)
        self.assertEquals(["id", "name", "works"], sorted(s.data.keys()))

    def test_render_form_list(self):
        s = api.FormInnerSerializer(self.f)
        self.assertEquals(["id", "name"], sorted(s.data.keys()))

    def test_instrument_detail_url(self):
        resp = self.apiclient.get("/api/makam/form/1494b665-8b67-430f-b6e6-efdcd42ddd3f")
        self.assertEqual(200, resp.status_code)

    def test_instrument_list_url(self):
        resp = self.apiclient.get("/api/makam/form")
        self.assertEqual(200, resp.status_code)
        self.assertEqual(1, len(resp.data["results"]))

class UsulTest(ApiTestCase):
    def setUp(self):
        super(UsulTest, self).setUp()
        self.u = models.Usul.objects.create(name="usul", uuid="d5e15ee7-e6c3-4148-845c-8e7610c619e9")

    def test_render_usul_detail(self):
        s = api.UsulDetailSerializer(self.u)
        self.assertEquals(["gazels", "id", "name", "taksims", "works"], sorted(s.data.keys()))

    def test_render_usul_list(self):
        s = api.UsulInnerSerializer(self.u)
        self.assertEquals(["id", "name"], sorted(s.data.keys()))

    def test_instrument_detail_url(self):
        resp = self.apiclient.get("/api/makam/usul/d5e15ee7-e6c3-4148-845c-8e7610c619e9")
        self.assertEqual(200, resp.status_code)

    def test_instrument_list_url(self):
        resp = self.apiclient.get("/api/makam/usul")
        self.assertEqual(200, resp.status_code)
        self.assertEqual(1, len(resp.data["results"]))

