import json
import uuid

from django.contrib import auth
from django.contrib.auth.models import Permission
from django.test import TestCase
from rest_framework.renderers import JSONRenderer
from rest_framework.test import APIClient

import data
from makam import api, models


class ApiTestCase(TestCase):
    def setUp(self):
        self.a = models.Artist.objects.create(name="Artist", mbid="a484bcbc-c0d9-468a-952c-9938d5811f85")

        self.coll1id = str(uuid.uuid4())
        self.col = data.models.Collection.objects.create(collectionid=self.coll1id, name="collection 1", permission="U")
        self.r = models.Release.objects.create(
            collection=self.col, title="Rel", mbid="805a3604-92e6-482f-a0e3-6620c4523d7a"
        )

        self.rec = models.Recording.objects.create(title="recording", mbid="2a599dee-db7d-48fd-9a34-fd4e1023cfcc")
        models.ReleaseRecording.objects.create(release=self.r, recording=self.rec, track=1)

        self.coll2id = str(uuid.uuid4())
        self.col2 = data.models.Collection.objects.create(
            collectionid=self.coll2id, name="collection 2", permission="R"
        )
        self.r2 = models.Release.objects.create(
            collection=self.col2, title="Rel 2", mbid="663cbe20-e8e1-11e4-9964-0002a5d5c51b"
        )

        self.rec2 = models.Recording.objects.create(title="recording 2", mbid="b287fe20-e8e1-11e4-bf83-0002a5d5c51b")
        models.ReleaseRecording.objects.create(release=self.r2, recording=self.rec2, track=1)

        self.coll3id = str(uuid.uuid4())
        self.col3 = data.models.Collection.objects.create(
            collectionid=self.coll3id, name="collection 3", permission="S"
        )
        self.r3 = models.Release.objects.create(
            collection=self.col3, title="Rel 3", mbid="cbe1ba35-8758-4a7d-9811-70bc48f41734"
        )

        self.rec3 = models.Recording.objects.create(title="recording 3", mbid="34275e18-0aef-4fa5-9618-b5938cb73a24")
        models.ReleaseRecording.objects.create(release=self.r3, recording=self.rec3, track=1)

        self.r.artists.add(self.a)
        self.r2.artists.add(self.a)
        self.r3.artists.add(self.a)

        self.staffuser = auth.models.User.objects.create_user("staffuser")
        self.staffuser.is_staff = True
        self.staffuser.save()

        permission = Permission.objects.get(codename="access_restricted")
        self.restricteduser = auth.models.User.objects.create_user("restricteduser")
        self.restricteduser.user_permissions.add(permission)
        self.restricteduser.save()

        self.normaluser = auth.models.User.objects.create_user("normaluser")

        self.apiclient = APIClient()
        self.apiclient.force_authenticate(user=self.staffuser)


class ArtistTest(ApiTestCase):
    def test_render_artist_detail(self):
        response = self.apiclient.get("/api/makam/artist/a484bcbc-c0d9-468a-952c-9938d5811f85")
        data = response.data

        keys = sorted(data.keys())
        self.assertEqual(["instruments", "mbid", "name", "releases"], keys)

    def test_render_artist_list(self):
        s = api.ArtistInnerSerializer(self.a)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        expected = {"name": "Artist", "mbid": "a484bcbc-c0d9-468a-952c-9938d5811f85"}
        self.assertEqual(expected, data)

    def test_artist_detail_url(self):
        resp = self.apiclient.get("/api/makam/artist/a484bcbc-c0d9-468a-952c-9938d5811f85")
        self.assertEqual(200, resp.status_code)

    def test_artist_list_url(self):
        resp = self.apiclient.get("/api/makam/artist")
        self.assertEqual(200, resp.status_code)
        self.assertEqual(1, len(resp.data["results"]))

    def test_artist_normal_collection(self):
        client = APIClient()
        client.force_authenticate(user=self.normaluser)

        # With the normal user we only get the unrestricted collection's releases
        collections = self.coll1id
        response = client.get(
            "/api/makam/artist/a484bcbc-c0d9-468a-952c-9938d5811f85", HTTP_DUNYA_COLLECTION=collections
        )
        data = response.data
        self.assertEqual(1, len(data["releases"]))
        self.assertEqual("805a3604-92e6-482f-a0e3-6620c4523d7a", data["releases"][0]["mbid"])

        # Even if they ask for restricted collection, only the normal ones
        collections = f"{self.coll1id}, {self.coll3id}"
        response = client.get(
            "/api/makam/artist/a484bcbc-c0d9-468a-952c-9938d5811f85", HTTP_DUNYA_COLLECTION=collections
        )
        data = response.data
        self.assertEqual(1, len(data["releases"]))

    def test_artist_collections_staff(self):
        # a staff user can choose if they see normal releases
        client = APIClient()
        client.force_authenticate(user=self.staffuser)
        collections = self.coll1id
        response = client.get(
            "/api/makam/artist/a484bcbc-c0d9-468a-952c-9938d5811f85", HTTP_DUNYA_COLLECTION=collections
        )
        data = response.data
        self.assertEqual(1, len(data["releases"]))

        # or restricted collections too
        collections = f"{self.coll3id}, {self.coll1id}"
        response = client.get(
            "/api/makam/artist/a484bcbc-c0d9-468a-952c-9938d5811f85", HTTP_DUNYA_COLLECTION=collections
        )
        data = response.data
        self.assertEqual(2, len(data["releases"]))
        self.assertEqual("805a3604-92e6-482f-a0e3-6620c4523d7a", data["releases"][0]["mbid"])
        self.assertEqual("cbe1ba35-8758-4a7d-9811-70bc48f41734", data["releases"][1]["mbid"])

    def test_artist_collections_restricted(self):
        # a restricted user can choose if they see normal releases
        client = APIClient()
        client.force_authenticate(user=self.restricteduser)
        collections = self.coll1id
        response = client.get(
            "/api/makam/artist/a484bcbc-c0d9-468a-952c-9938d5811f85", HTTP_DUNYA_COLLECTION=collections
        )
        data = response.data
        self.assertEqual(1, len(data["releases"]))

        # or restricted collections too
        collections = f"{self.coll1id}, {self.coll2id}"
        response = client.get(
            "/api/makam/artist/a484bcbc-c0d9-468a-952c-9938d5811f85", HTTP_DUNYA_COLLECTION=collections
        )
        data = response.data
        self.assertEqual(2, len(data["releases"]))
        self.assertEqual("805a3604-92e6-482f-a0e3-6620c4523d7a", data["releases"][0]["mbid"])
        self.assertEqual("663cbe20-e8e1-11e4-9964-0002a5d5c51b", data["releases"][1]["mbid"])


class ComposerTest(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.c = models.Composer.objects.create(name="Composer", mbid="392fa7ab-f87d-4a07-9c83-bd23130e711b")

    def test_render_composer_detail(self):
        s = api.ComposerDetailSerializer(self.c)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        self.assertEqual(["lyric_works", "mbid", "name", "works"], sorted(data.keys()))

    def test_render_composer_list(self):
        s = api.ComposerInnerSerializer(self.c)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        expected = {"name": "Composer", "mbid": "392fa7ab-f87d-4a07-9c83-bd23130e711b"}
        self.assertEqual(expected, data)

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
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        self.assertEqual(["image", "mbid", "recordings", "release_artists", "title", "year"], sorted(data.keys()))

    def test_render_release_list(self):
        s = api.ReleaseInnerSerializer(self.r)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        self.assertEqual(["mbid", "title"], sorted(data.keys()))

    def test_release_detail_url(self):
        resp = self.apiclient.get("/api/makam/release/805a3604-92e6-482f-a0e3-6620c4523d7a")
        self.assertEqual(200, resp.status_code)

    def test_release_list_url(self):
        resp = self.apiclient.get("/api/makam/release")
        self.assertEqual(200, resp.status_code)
        self.assertEqual(3, len(resp.data["results"]))

    def test_release_list_collection(self):
        """Staff members will see releases from restricted collections in
        this list if they ask for them"""
        client = APIClient()
        client.force_authenticate(user=self.staffuser)

        collections = self.coll3id
        response = client.get("/api/makam/release", HTTP_DUNYA_COLLECTION=collections)

        data = response.data
        self.assertEqual(1, len(data["results"]))

        collections = f"{self.coll3id}, {self.coll2id}"
        response = client.get("/api/makam/release", HTTP_DUNYA_COLLECTION=collections)
        data = response.data

        self.assertEqual(2, len(data["results"]))

        # A normal user passing a collection over header parameter will still only
        # get 1 release
        client.force_authenticate(user=self.normaluser)
        collections = f"{self.coll3id}, {self.coll1id}"
        response = client.get("/api/makam/release", HTTP_DUNYA_COLLECTION=collections)
        data = response.data
        self.assertEqual(1, len(data["results"]))

        # A restricted user using collection header will get the release associated
        # with the restricted access collection
        client.force_authenticate(user=self.restricteduser)
        collections = f"{self.coll3id}, {self.coll1id}, {self.coll2id}"
        response = client.get("/api/makam/release", HTTP_DUNYA_COLLECTION=collections)
        data = response.data
        self.assertEqual(2, len(data["results"]))


class RecordingTest(ApiTestCase):
    def setUp(self):
        super().setUp()

    def test_render_recording_detail(self):
        resp = self.apiclient.get("/api/makam/recording/2a599dee-db7d-48fd-9a34-fd4e1023cfcc")
        self.assertEqual(
            ["artists", "makamlist", "mbid", "performers", "releases", "title", "usullist", "works"],
            sorted(resp.data.keys()),
        )

    def test_render_recording_list(self):
        s = api.RecordingInnerSerializer(self.r)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        self.assertEqual(["artists", "mbid", "title"], sorted(data.keys()))

    def test_recording_detail_url(self):
        resp = self.apiclient.get("/api/makam/recording/2a599dee-db7d-48fd-9a34-fd4e1023cfcc")
        self.assertEqual(200, resp.status_code)

    def test_recording_list_url(self):
        resp = self.apiclient.get("/api/makam/recording")
        self.assertEqual(200, resp.status_code)
        self.assertEqual(3, len(resp.data["results"]))

    def test_recording_list_collection(self):
        """Staff members will see recordings from restricted collections in
        this list too"""
        client = APIClient()
        client.force_authenticate(user=self.staffuser)

        collections = self.coll1id
        response = client.get("/api/makam/recording", HTTP_DUNYA_COLLECTION=collections)
        data = response.data
        self.assertEqual(1, len(data["results"]))
        response = client.get("/api/makam/recording")
        data = response.data
        self.assertEqual(3, len(data["results"]))

        # A restricted user passing a restricted collection over the header parameter will
        # get 1 recording
        client.force_authenticate(user=self.restricteduser)

        collections = self.coll2id
        response = client.get("/api/makam/recording", HTTP_DUNYA_COLLECTION=collections)
        data = response.data
        self.assertEqual(1, len(data["results"]))

        # A normal user passing a collection over the header parameter will still only
        # get 1 recording
        client.force_authenticate(user=self.normaluser)
        collections = self.coll1id
        response = client.get("/api/makam/recording", HTTP_DUNYA_COLLECTION=collections)
        data = response.data
        self.assertEqual(1, len(data["results"]))


class WorkTest(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.w = models.Work.objects.create(title="work", mbid="5f41f3ed-6c48-403f-ba6c-3e810b58295c")

    def test_render_work_detail(self):
        resp = self.apiclient.get("/api/makam/work/5f41f3ed-6c48-403f-ba6c-3e810b58295c")
        fields = ["mbid", "title", "composers", "lyricists", "makams", "forms", "usuls", "recordings"]
        self.assertEqual(sorted(fields), sorted(resp.data.keys()))

    def test_render_work_list(self):
        s = api.WorkInnerSerializer(self.w)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        self.assertEqual(["mbid", "title"], sorted(data.keys()))

    def test_recording_detail_url(self):
        resp = self.apiclient.get("/api/makam/work/5f41f3ed-6c48-403f-ba6c-3e810b58295c")
        self.assertEqual(200, resp.status_code)

    def test_recording_list_url(self):
        resp = self.apiclient.get("/api/makam/work")
        self.assertEqual(200, resp.status_code)
        self.assertEqual(1, len(resp.data["results"]))


class InstrumentTest(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.uuid = "1f20598b-cf3a-4253-a576-d8025abb47fd"
        self.i1 = models.Instrument.objects.create(pk=3, name="inst1", mbid=self.uuid)
        self.rec1 = models.Recording.objects.create(title="rec1")
        self.a1 = models.Artist.objects.create(name="a1")
        models.InstrumentPerformance.objects.create(recording=self.rec1, artist=self.a1, instrument=self.i1)

    def test_render_instrument_detail(self):
        s = api.InstrumentDetailSerializer(self.i1)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        self.assertEqual(["artists", "mbid", "name"], sorted(data.keys()))
        self.assertEqual(1, len(data["artists"]))

    def test_render_instrument_list(self):
        s = api.InstrumentInnerSerializer(self.i1)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        self.assertEqual(["mbid", "name"], sorted(data.keys()))

    def test_instrument_detail_url(self):
        resp = self.apiclient.get(f"/api/makam/instrument/{self.uuid}")
        self.assertEqual(200, resp.status_code)

    def test_instrument_list_url(self):
        resp = self.apiclient.get("/api/makam/instrument")
        self.assertEqual(200, resp.status_code)
        self.assertEqual(1, len(resp.data["results"]))


class MakamTest(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.m = models.Makam.objects.create(name="makam", uuid="9c9b77cc-e357-402f-9278-2c5ed49e06b7")

    def test_makam_by_uuid(self):
        resp = self.apiclient.get(f"/api/makam/makam/{self.m.uuid}")
        self.assertEqual(200, resp.status_code)
        self.assertEqual(self.m.name, resp.data["name"])

    def test_render_makam_detail(self):
        s = api.MakamDetailSerializer(self.m)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        self.assertEqual(["gazels", "name", "symtr_key", "taksims", "uuid", "works"], sorted(data.keys()))

    def test_render_makam_list(self):
        s = api.MakamInnerSerializer(self.m)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        self.assertEqual(["name", "uuid"], sorted(data.keys()))

    def test_instrument_detail_url(self):
        resp = self.apiclient.get("/api/makam/makam/9c9b77cc-e357-402f-9278-2c5ed49e06b7")
        self.assertEqual(200, resp.status_code)

    def test_instrument_list_url(self):
        resp = self.apiclient.get("/api/makam/makam")
        self.assertEqual(200, resp.status_code)
        self.assertEqual(1, len(resp.data["results"]))


class FormTest(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.f = models.Form.objects.create(name="form", uuid="1494b665-8b67-430f-b6e6-efdcd42ddd3f")

    def test_form_by_uuid(self):
        resp = self.apiclient.get(f"/api/makam/form/{self.f.uuid}")
        self.assertEqual(200, resp.status_code)

    def test_render_form_detail(self):
        s = api.FormDetailSerializer(self.f)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        self.assertEqual(["name", "uuid", "works"], sorted(data.keys()))

    def test_render_form_list(self):
        s = api.FormInnerSerializer(self.f)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        self.assertEqual(["name", "uuid"], sorted(data.keys()))

    def test_instrument_detail_url(self):
        resp = self.apiclient.get("/api/makam/form/1494b665-8b67-430f-b6e6-efdcd42ddd3f")
        self.assertEqual(200, resp.status_code)

    def test_instrument_list_url(self):
        resp = self.apiclient.get("/api/makam/form")
        self.assertEqual(200, resp.status_code)
        self.assertEqual(1, len(resp.data["results"]))


class UsulTest(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.u = models.Usul.objects.create(name="usul", uuid="d5e15ee7-e6c3-4148-845c-8e7610c619e9")

    def test_usul_by_uuid(self):
        resp = self.apiclient.get(f"/api/makam/usul/{self.u.uuid}")
        self.assertEqual(200, resp.status_code)
        self.assertEqual(self.u.name, resp.data["name"])

    def test_render_usul_detail(self):
        s = api.UsulDetailSerializer(self.u)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        self.assertEqual(["gazels", "name", "taksims", "uuid", "works"], sorted(data.keys()))

    def test_render_usul_list(self):
        s = api.UsulInnerSerializer(self.u)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        self.assertEqual(["name", "uuid"], sorted(data.keys()))

    def test_instrument_detail_url(self):
        resp = self.apiclient.get("/api/makam/usul/d5e15ee7-e6c3-4148-845c-8e7610c619e9")
        self.assertEqual(200, resp.status_code)

    def test_instrument_list_url(self):
        resp = self.apiclient.get("/api/makam/usul")
        self.assertEqual(200, resp.status_code)
        self.assertEqual(1, len(resp.data["results"]))


class SymbTrTest(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.s = models.SymbTr.objects.create(name="usul", uuid="d5e15ee7-e6c3-4148-4444-8e7610c65555")

    def test_render_symbtr_detail(self):
        s = api.SymbtrDetailSerializer(self.s)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        self.assertEqual(["name", "uuid"], sorted(data.keys()))

    def test_symbtr_detail_url(self):
        resp = self.apiclient.get("/api/makam/symbtr/d5e15ee7-e6c3-4148-4444-8e7610c65555")
        self.assertEqual(200, resp.status_code)

    def test_symbtr_list_url(self):
        resp = self.apiclient.get("/api/makam/symbtr")
        self.assertEqual(200, resp.status_code)
        self.assertEqual(1, len(resp.data["results"]))
