from django.test import TestCase
from django.contrib import auth
from rest_framework.test import APIClient

from hindustani import models
from hindustani import api

class ApiTestCase(TestCase):
    def setUp(self):
        self.staffuser = auth.models.User.objects.create_user("staffuser")
        self.staffuser.is_staff = True
        self.staffuser.save()

        self.apiclient = APIClient()
        self.apiclient.force_authenticate(user=self.staffuser)

class ArtistTest(ApiTestCase):
    def setUp(self):
        super(ArtistTest, self).setUp()
        self.a = models.Artist.objects.create(name="Foo", mbid="a484bcbc-c0d9-468a-952c-9938d5811f85")

    def test_render_artist_inner(self):
        s = api.ArtistInnerSerializer(self.a)
        expected = {"name": "Foo", "mbid": "a484bcbc-c0d9-468a-952c-9938d5811f85"}
        self.assertEquals(expected, s.data)

    def test_render_artist_detail(self):
        pass

    def test_artist_detail_url(self):
        resp = self.apiclient.get("/api/hindustani/artist/a484bcbc-c0d9-468a-952c-9938d5811f85")
        self.assertEqual(200, resp.status_code)

class ComposerTest(ApiTestCase):
    def setUp(self):
        super(ComposerTest, self).setUp()
        self.c = models.Composer.objects.create(name="Composer", mbid="8d61fc81-d3ac-43a3-bbec-dc00162ee87d")

    def test_render_composer_inner(self):
        s = api.ComposerInnerSerializer(self.c)
        self.assertEqual(['mbid', 'name'], sorted(s.data.keys()))

class RecordingTest(ApiTestCase):
    def setUp(self):
        super(RecordingTest, self).setUp()
        self.r = models.Recording.objects.create(title="recording", mbid="63ddd257-a92e-4c0c-b639-ce59e1e57a4a")

    def test_render_recording_inner(self):
        s = api.RecordingInnerSerializer(self.r)
        self.assertEqual(['mbid', 'title'], sorted(s.data.keys()))

    def test_render_recording_detail(self):
        s = api.RecordingDetailSerializer(self.r)
        expected = ['artists', 'forms', 'layas', 'mbid', 'raags', 'release', 'taals', 'title', 'works']
        self.assertEqual(expected, sorted(s.data.keys()))

    def test_recording_detail_url(self):
        resp = self.apiclient.get("/api/hindustani/recording/63ddd257-a92e-4c0c-b639-ce59e1e57a4a")
        self.assertEqual(200, resp.status_code)


class WorkTest(ApiTestCase):
    def setUp(self):
        super(WorkTest, self).setUp()
        self.w = models.Work.objects.create(title="Work", mbid="7c08c56d-504b-4c42-ac99-1ffaa76f9aa0")

    def test_render_work_inner(self):
        s = api.WorkInnerSerializer(self.w)
        self.assertEqual(['mbid', 'title'], sorted(s.data.keys()))

    def test_render_work_detail(self):
        s = api.WorkDetailSerializer(self.w)
        self.assertEqual(['mbid', 'recordings', 'title'], sorted(s.data.keys()))

    def test_work_detail_url(self):
        resp = self.apiclient.get("/api/hindustani/work/7c08c56d-504b-4c42-ac99-1ffaa76f9aa0")
        self.assertEqual(200, resp.status_code)

class RaagTest(ApiTestCase):
    def setUp(self):
        super(RaagTest, self).setUp()
        self.r = models.Raag.objects.create(name="raag", common_name="raag", uuid="3cecdb8e-2a54-4833-8049-b3d8060f7e32")

    def test_render_raag_inner(self):
        s = api.RaagInnerSerializer(self.r)
        self.assertEqual(['common_name', 'name', 'uuid'], sorted(s.data.keys()))

    def test_render_raag_detail(self):
        s = api.RaagDetailSerializer(self.r)
        expected = ['aliases', 'artists', 'common_name', 'composers', 'name', 'uuid']
        self.assertEqual(expected, sorted(s.data.keys()))

    def test_raag_detail_url(self):
        resp = self.apiclient.get("/api/hindustani/raag/3cecdb8e-2a54-4833-8049-b3d8060f7e32")
        self.assertEqual(200, resp.status_code)

class TaalTest(ApiTestCase):
    def setUp(self):
        super(TaalTest, self).setUp()
        self.t = models.Taal.objects.create(name="taal", common_name="taal", uuid="4f55fa34-5f77-4570-888c-0596cfc8a81a")

    def test_render_taal_inner(self):
        s = api.TaalInnerSerializer(self.t)
        self.assertEqual(['common_name', 'name', 'uuid'], sorted(s.data.keys()))

    def test_render_taal_detail(self):
        s = api.TaalDetailSerializer(self.t)
        expected = ['aliases', 'common_name', 'composers', 'name', 'uuid']
        self.assertEqual(expected, sorted(s.data.keys()))

    def test_taal_detail_url(self):
        resp = self.apiclient.get("/api/hindustani/taal/4f55fa34-5f77-4570-888c-0596cfc8a81a")
        self.assertEqual(200, resp.status_code)

class FormTest(ApiTestCase):
    def setUp(self):
        super(FormTest, self).setUp()
        self.f = models.Form.objects.create(name="form", common_name="form", uuid="29847751-350b-4db2-9d18-630769ee2c6c")

    def test_render_form_inner(self):
        s = api.FormInnerSerializer(self.f)
        self.assertEqual(['common_name', 'name', 'uuid'], sorted(s.data.keys()))

    def test_render_form_detail(self):
        s = api.FormDetailSerializer(self.f)
        expected = ['aliases', 'artists', 'common_name', 'name', 'recordings', 'uuid']
        self.assertEqual(expected, sorted(s.data.keys()))

    def test_taal_detail_url(self):
        resp = self.apiclient.get("/api/hindustani/form/29847751-350b-4db2-9d18-630769ee2c6c")
        self.assertEqual(200, resp.status_code)

class LayaTest(ApiTestCase):
    def setUp(self):
        super(LayaTest, self).setUp()
        self.l = models.Laya.objects.create(name="laya", common_name="laya", uuid="e5d56b8c-f791-430a-ac2b-4c75f81a87c5")

    def test_render_laya_inner(self):
        s = api.LayaInnerSerializer(self.l)
        self.assertEqual(['common_name', 'name', 'uuid'], sorted(s.data.keys()))

    def test_render_laya_detail(self):
        s = api.LayaDetailSerializer(self.l)
        expected = ['aliases', 'common_name', 'name', 'recordings', 'uuid']
        self.assertEqual(expected, sorted(s.data.keys()))

    def test_laya_detail_url(self):
        resp = self.apiclient.get("/api/hindustani/laya/e5d56b8c-f791-430a-ac2b-4c75f81a87c5")
        self.assertEqual(200, resp.status_code)

class ReleaseTest(ApiTestCase):
    pass

class InstrumentTest(ApiTestCase):
    pass

