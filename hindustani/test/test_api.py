from django.test import TestCase
from django.contrib import auth
from rest_framework.test import APIClient
from rest_framework.renderers import JSONRenderer
from django.contrib.auth.models import Permission
import uuid
import json

import data
from hindustani import models
from hindustani import api


class ApiTestCase(TestCase):
    def setUp(self):
        self.staffuser = auth.models.User.objects.create_user("staffuser")
        self.staffuser.is_staff = True
        self.staffuser.save()

        permission = Permission.objects.get(codename="access_restricted")
        self.restricteduser = auth.models.User.objects.create_user("restricteduser")
        self.restricteduser.user_permissions.add(permission)
        self.restricteduser.save()

        self.apiclient = APIClient()
        self.apiclient.force_authenticate(user=self.staffuser)


class ArtistTest(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.i = models.Instrument.objects.create(name="Violin")
        self.a1 = models.Artist.objects.create(
            name="Artist1", mbid="a484bcbc-c0d9-468a-952c-9938d5811f85", main_instrument=self.i
        )
        self.a2 = models.Artist.objects.create(name="Artist2", main_instrument=self.i)
        self.a3 = models.Artist.objects.create(name="Artist3", main_instrument=self.i)

        self.coll1id = str(uuid.uuid4())
        self.col1 = data.models.Collection.objects.create(
            name="collection 1", collectionid=self.coll1id, permission="U"
        )
        self.rel1 = models.Release.objects.create(collection=self.col1, title="Release1")
        self.r1 = models.Recording.objects.create(title="Recording1")
        models.ReleaseRecording.objects.create(release=self.rel1, recording=self.r1, track=1, disc=1, disctrack=1)
        # artist 1 on release
        self.rel1.artists.add(self.a1)
        # artist 2, 3 on recording rel
        models.InstrumentPerformance.objects.create(instrument=self.i, artist=self.a2, recording=self.r1)
        models.InstrumentPerformance.objects.create(instrument=self.i, artist=self.a3, recording=self.r1)

        self.coll2id = str(uuid.uuid4())
        self.col2 = data.models.Collection.objects.create(
            name="collection 2", collectionid=self.coll2id, permission="R"
        )
        self.rel2 = models.Release.objects.create(collection=self.col2, title="Release2")
        self.r2 = models.Recording.objects.create(title="Recording2")
        self.r3 = models.Recording.objects.create(title="Recording3")
        models.ReleaseRecording.objects.create(release=self.rel2, recording=self.r2, track=1, disc=1, disctrack=1)
        models.ReleaseRecording.objects.create(release=self.rel2, recording=self.r3, track=2, disc=1, disctrack=2)
        # artist 2 on release
        self.rel2.artists.add(self.a2)
        # artist 1 & 3 on r2, but only a1 on r3
        models.InstrumentPerformance.objects.create(instrument=self.i, artist=self.a1, recording=self.r2)
        models.InstrumentPerformance.objects.create(instrument=self.i, artist=self.a3, recording=self.r2)
        models.InstrumentPerformance.objects.create(instrument=self.i, artist=self.a1, recording=self.r3)

        # A release from restricted collection, with a2
        self.coll3id = str(uuid.uuid4())
        self.col3 = data.models.Collection.objects.create(
            name="collection 3", collectionid=self.coll3id, permission="S"
        )
        self.rel3 = models.Release.objects.create(collection=self.col3, title="Release3")
        self.r4 = models.Recording.objects.create(title="Recording4")
        models.ReleaseRecording.objects.create(release=self.rel3, recording=self.r4, track=1, disc=1, disctrack=1)
        self.rel3.artists.add(self.a2)

    def test_render_artist_inner(self):
        s = api.ArtistInnerSerializer(self.a1)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        expected = {"name": "Artist1", "mbid": "a484bcbc-c0d9-468a-952c-9938d5811f85"}
        self.assertEqual(expected, data)

    def test_render_artist_detail(self):
        pass

    def test_artist_detail_url(self):
        resp = self.apiclient.get("/api/hindustani/artist/a484bcbc-c0d9-468a-952c-9938d5811f85")
        self.assertEqual(200, resp.status_code)

    def test_recording_get_artists(self):
        """The artists that performed on a recording
        - Artists with performance relationship on the recording
        - Artists with perf rel on the release this rec is part of
        - Primary artists of the release
        """
        artists = self.r1.all_artists()
        self.assertEqual(3, len(artists))

        artists = self.r2.all_artists()
        self.assertEqual(3, len(artists))

        artists = self.r3.all_artists()
        self.assertEqual(2, len(artists))

    def test_release_get_artists(self):
        """Artists who performed on a release
        - if they are a primary artist
        - If they're a relationship on the release
        - If they're a relationship on a track
        """
        artists = self.rel1.performers()
        self.assertEqual(3, len(artists))

        artists = self.rel2.performers()
        self.assertEqual(3, len(artists))

    def test_artist_get_releases(self):
        """Releasess performed by an artist"""
        c = self.a1.releases()
        self.assertEqual(1, len(c))
        c = self.a2.releases()
        self.assertEqual(1, len(c))
        c = self.a3.releases()
        self.assertEqual(1, len(c))

        coll4id = str(uuid.uuid4())
        col = data.models.Collection.objects.create(name="collection 4", collectionid=coll4id, permission="U")
        rel = models.Release.objects.create(collection=col, title="Other release")
        rel.artists.add(self.a3)
        c = self.a3.releases()
        self.assertEqual(2, len(c))

    def test_artist_group_get_releases(self):
        """If you're in a group, you performed in that group's concerts"""
        grp = models.Artist.objects.create(name="Group")
        art = models.Artist.objects.create(name="Artist")
        grp.group_members.add(art)
        coll4id = str(uuid.uuid4())
        col = data.models.Collection.objects.create(name="collection 4", collectionid=coll4id, permission="U")
        rel = models.Release.objects.create(collection=col, title="Other concert")
        c = art.releases()
        self.assertEqual(0, len(c))
        rel.artists.add(grp)
        c = art.releases()
        self.assertEqual(1, len(c))

    def test_artist_restr_collection_releases(self):
        """If you ask for a restricted collection you get an extra release"""

        collections = [self.coll1id, self.coll2id, self.coll3id]
        c = self.a2.releases(collection_ids=collections, permission=["U", "R", "S"])
        self.assertEqual(3, len(c))

    def test_artist_get_recordings(self):
        """Recordings performed by an artist
        - explicit recording relationships
        - Also if they're a release primary artist or have a rel
        """
        collections = [self.coll1id, self.coll2id, self.coll3id]
        recs = self.a1.recordings(collection_ids=collections, permission=["U", "R", "S"])
        self.assertEqual(3, len(recs))
        recs = self.a2.recordings(collection_ids=collections, permission=["U", "R", "S"])
        self.assertEqual(4, len(recs))
        # A3 is not on recording3
        recs = self.a3.recordings(collection_ids=collections, permission=["U", "R", "S"])
        self.assertEqual(2, len(recs))

    def test_artist_collection_recordings(self):
        collections = [self.coll1id, self.coll2id, self.coll3id]
        recs = self.a2.recordings(collection_ids=collections, permission=["U", "R", "S"])
        self.assertEqual(4, len(recs))


class ComposerTest(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.c = models.Composer.objects.create(name="Composer", mbid="8d61fc81-d3ac-43a3-bbec-dc00162ee87d")

    def test_render_composer_inner(self):
        s = api.ComposerInnerSerializer(self.c)
        self.assertEqual(["mbid", "name"], sorted(s.data.keys()))


class RecordingTest(ApiTestCase):
    def setUp(self):
        super().setUp()

        self.coll1id = str(uuid.uuid4())
        self.col1 = data.models.Collection.objects.create(
            collectionid=self.coll1id, name="collection 1", permission="U"
        )
        self.relnormal = models.Release.objects.create(
            collection=self.col1, title="somerelease", mbid="c8296944-74f6-4277-94c9-9481d7a8ba81"
        )

        self.normaluser = auth.models.User.objects.create_user("normaluser")

        self.coll2id = str(uuid.uuid4())
        self.col2 = data.models.Collection.objects.create(
            collectionid=self.coll2id, name="collection 2", permission="S"
        )
        self.relstaff = models.Release.objects.create(
            collection=self.col2, title="somerelease2", mbid="2c7638f6-d172-4dcd-bca7-06f912e0f09e"
        )

        self.coll3id = str(uuid.uuid4())  # adf4
        self.col3 = data.models.Collection.objects.create(
            collectionid=self.coll3id, name="collection 3", permission="R"
        )
        self.relrestr = models.Release.objects.create(
            collection=self.col3, title="somerelease3", mbid="b5c3a883-67f5-4d01-982f-6c70f3569191"
        )

        self.wnormal = models.Work.objects.create(title="normal work", mbid="7ed898bc-fa11-41ae-b1c9-913d96c40e2b")
        self.wrestricted = models.Work.objects.create(
            title="restricted work", mbid="b4e100b4-024f-4ed8-8942-9150e99d4c80"
        )
        self.wstaff = models.Work.objects.create(title="Work", mbid="7c08c56d-504b-4c42-ac99-1ffaa76f9aa0")

        self.rnormal = models.Recording.objects.create(
            title="normal recording", mbid="dcf14452-e13e-450f-82c2-8ae705a58971"
        )
        self.rrestricted = models.Recording.objects.create(
            title="restricted recording", mbid="34275e18-0aef-4fa5-9618-b5938cb73a24"
        )
        self.rstaff = models.Recording.objects.create(
            title="staff recording", mbid="b287fe20-e8e1-11e4-bf83-0002a5d5c51b"
        )

        models.WorkTime.objects.create(work=self.wnormal, recording=self.rnormal, sequence=1)
        models.WorkTime.objects.create(work=self.wrestricted, recording=self.rrestricted, sequence=1)
        models.WorkTime.objects.create(work=self.wstaff, recording=self.rstaff, sequence=1)

        models.ReleaseRecording.objects.create(
            release=self.relnormal, recording=self.rnormal, track=1, disc=1, disctrack=1
        )
        models.ReleaseRecording.objects.create(
            release=self.relrestr, recording=self.rrestricted, track=1, disc=1, disctrack=1
        )
        models.ReleaseRecording.objects.create(
            release=self.relstaff, recording=self.rstaff, track=1, disc=1, disctrack=1
        )

    def test_render_recording_inner(self):
        s = api.RecordingInnerSerializer(self.rnormal)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        self.assertEqual(["mbid", "title"], sorted(data.keys()))

    def test_render_recording_detail(self):
        resp = self.apiclient.get("/api/hindustani/recording/dcf14452-e13e-450f-82c2-8ae705a58971")
        expected = [
            "album_artists",
            "artists",
            "forms",
            "layas",
            "length",
            "mbid",
            "raags",
            "release",
            "taals",
            "title",
            "works",
        ]
        self.assertEqual(expected, sorted(resp.data.keys()))

    def test_recording_detail_url(self):
        resp = self.apiclient.get("/api/hindustani/recording/dcf14452-e13e-450f-82c2-8ae705a58971")
        self.assertEqual(200, resp.status_code)

    def test_recording_list_collection_bad_uuid(self):
        """Returns error if Dunya-Collection header is invalid"""
        client = APIClient()
        client.force_authenticate(user=self.staffuser)

        response = client.get("/api/hindustani/recording", **{"HTTP_DUNYA_COLLECTION": "not-a-uuid"})
        self.assertEqual(response.status_code, 400)

    def test_recording_list_collection(self):
        """Staff members will see recordings from restricted collections in
        this list too"""
        client = APIClient()
        client.force_authenticate(user=self.staffuser)

        collections = self.coll1id
        response = client.get("/api/hindustani/recording", **{"HTTP_DUNYA_COLLECTION": collections})
        data = response.data
        self.assertEqual(1, len(data["results"]))
        response = client.get("/api/hindustani/recording")
        data = response.data
        self.assertEqual(3, len(data["results"]))

        # A restricted user passing a restricted collection over the header parameter will
        # get 1 recording
        client.force_authenticate(user=self.staffuser)

        collections = self.coll3id
        response = client.get("/api/hindustani/recording", **{"HTTP_DUNYA_COLLECTION": collections})
        data = response.data
        self.assertEqual(1, len(data["results"]))

        # A normal user passing a collection over the header parameter will still only
        # get 1 recording
        client.force_authenticate(user=self.normaluser)
        response = client.get("/api/hindustani/recording")
        data = response.data
        self.assertEqual(1, len(data["results"]))


class WorkTest(ApiTestCase):
    def setUp(self):
        super().setUp()

        self.coll1id = str(uuid.uuid4())
        self.col1 = data.models.Collection.objects.create(
            collectionid=self.coll1id, name="collection 1", permission="U"
        )
        self.relnormal = models.Release.objects.create(
            collection=self.col1, title="somerelease", mbid="c8296944-74f6-4277-94c9-9481d7a8ba81"
        )

        self.normaluser = auth.models.User.objects.create_user("normaluser")

        self.coll2id = str(uuid.uuid4())
        self.col2 = data.models.Collection.objects.create(
            collectionid=self.coll2id, name="collection 2", permission="S"
        )
        self.relstaff = models.Release.objects.create(
            collection=self.col2, title="somerelease2", mbid="2c7638f6-d172-4dcd-bca7-06f912e0f09e"
        )

        self.coll3id = str(uuid.uuid4())
        self.col3 = data.models.Collection.objects.create(
            collectionid=self.coll3id, name="collection 3", permission="R"
        )
        self.relrestr = models.Release.objects.create(
            collection=self.col3, title="somerelease3", mbid="b5c3a883-67f5-4d01-982f-6c70f3569191"
        )

        self.wnormal = models.Work.objects.create(title="normal work", mbid="7ed898bc-fa11-41ae-b1c9-913d96c40e2b")
        self.wrestricted = models.Work.objects.create(
            title="restricted work", mbid="b4e100b4-024f-4ed8-8942-9150e99d4c80"
        )
        self.wstaff = models.Work.objects.create(title="Work", mbid="7c08c56d-504b-4c42-ac99-1ffaa76f9aa0")

        self.rnormal = models.Recording.objects.create(
            title="normal recording", mbid="dcf14452-e13e-450f-82c2-8ae705a58971"
        )
        self.rrestricted = models.Recording.objects.create(
            title="restricted recording", mbid="34275e18-0aef-4fa5-9618-b5938cb73a24"
        )
        self.rstaff = models.Recording.objects.create(
            title="staff recording", mbid="b287fe20-e8e1-11e4-bf83-0002a5d5c51b"
        )

        models.WorkTime.objects.create(work=self.wnormal, recording=self.rnormal, sequence=1)
        models.WorkTime.objects.create(work=self.wrestricted, recording=self.rrestricted, sequence=1)
        models.WorkTime.objects.create(work=self.wstaff, recording=self.rstaff, sequence=1)

        models.ReleaseRecording.objects.create(
            release=self.relnormal, recording=self.rnormal, track=1, disc=1, disctrack=1
        )
        models.ReleaseRecording.objects.create(
            release=self.relrestr, recording=self.rrestricted, track=1, disc=1, disctrack=1
        )
        models.ReleaseRecording.objects.create(
            release=self.relstaff, recording=self.rstaff, track=1, disc=1, disctrack=1
        )

    def test_render_work_inner(self):
        s = api.WorkInnerSerializer(self.wnormal)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        self.assertEqual(["mbid", "title"], sorted(data.keys()))

    def test_render_work_detail(self):
        resp = self.apiclient.get("/api/hindustani/work/7c08c56d-504b-4c42-ac99-1ffaa76f9aa0")
        self.assertEqual(["mbid", "recordings", "title"], sorted(resp.data.keys()))

    def test_work_detail_url(self):
        resp = self.apiclient.get("/api/hindustani/work/7c08c56d-504b-4c42-ac99-1ffaa76f9aa0")
        self.assertEqual(200, resp.status_code)

    def test_work_collection_recordings_staff(self):
        client = APIClient()
        client.force_authenticate(user=self.staffuser)

        collections = f"{self.coll1id}"
        response = client.get(
            "/api/hindustani/work/7ed898bc-fa11-41ae-b1c9-913d96c40e2b", **{"HTTP_DUNYA_COLLECTION": collections}
        )
        data = response.data
        self.assertEqual(1, len(data["recordings"]))

        # Collection that doesn't exist
        collections = str(uuid.uuid4())
        response = client.get(
            "/api/hindustani/work/b4e100b4-024f-4ed8-8942-9150e99d4c80", **{"HTTP_DUNYA_COLLECTION": collections}
        )
        data = response.data
        self.assertEqual(0, len(data["recordings"]))

        collections = f"{self.coll3id}, {self.coll1id}"
        response = client.get(
            "/api/hindustani/work/b4e100b4-024f-4ed8-8942-9150e99d4c80", **{"HTTP_DUNYA_COLLECTION": collections}
        )
        data = response.data
        self.assertEqual(1, len(data["recordings"]))

    def test_work_collection_recordings_restricted(self):
        client = APIClient()
        client.force_authenticate(user=self.restricteduser)

        collections = f"{self.coll1id}"
        response = client.get(
            "/api/hindustani/work/7ed898bc-fa11-41ae-b1c9-913d96c40e2b", **{"HTTP_DUNYA_COLLECTION": collections}
        )
        data = response.data
        self.assertEqual(1, len(data["recordings"]))

        collections = f"{self.coll2id}"
        response = client.get(
            "/api/hindustani/work/b4e100b4-024f-4ed8-8942-9150e99d4c80", **{"HTTP_DUNYA_COLLECTION": collections}
        )
        data = response.data
        self.assertEqual(0, len(data["recordings"]))

        collections = f"{self.coll3id}"
        response = client.get(
            "/api/hindustani/work/b4e100b4-024f-4ed8-8942-9150e99d4c80", **{"HTTP_DUNYA_COLLECTION": collections}
        )
        data = response.data
        self.assertEqual(1, len(data["recordings"]))

    def test_work_collection_recordings_nostaff(self):
        client = APIClient()
        client.force_authenticate(user=self.normaluser)

        collections = f"{self.coll1id}"
        response = client.get(
            "/api/hindustani/work/7ed898bc-fa11-41ae-b1c9-913d96c40e2b", **{"HTTP_DUNYA_COLLECTION": collections}
        )
        data = response.data
        self.assertEqual(1, len(data["recordings"]))

        response = client.get("/api/hindustani/work/b4e100b4-024f-4ed8-8942-9150e99d4c80")
        data = response.data
        self.assertEqual(0, len(data["recordings"]))

        collections = f"{str(uuid.uuid4())}, {self.coll2id}, {self.coll1id}"
        response = client.get(
            "/api/hindustani/work/b4e100b4-024f-4ed8-8942-9150e99d4c80", **{"HTTP_DUNYA_COLLECTION": collections}
        )
        data = response.data
        self.assertEqual(0, len(data["recordings"]))


class RaagTest(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.r = models.Raag.objects.create(
            name="raag", common_name="raag", uuid="3cecdb8e-2a54-4833-8049-b3d8060f7e32"
        )

    def test_raag_by_id(self):
        good_id = self.r.id
        resp = self.apiclient.get(f"/api/hindustani/raag/{good_id}")
        self.assertRedirects(resp, "/api/hindustani/raag/3cecdb8e-2a54-4833-8049-b3d8060f7e32", status_code=301)

        bad_id = good_id + 1
        resp = self.apiclient.get(f"/api/hindustani/raag/{bad_id}")
        self.assertEqual(404, resp.status_code)

    def test_render_raag_inner(self):
        s = api.RaagInnerSerializer(self.r)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        self.assertEqual(["common_name", "name", "uuid"], sorted(data.keys()))

    def test_render_raag_detail(self):
        s = api.RaagDetailSerializer(self.r)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        expected = ["aliases", "artists", "common_name", "composers", "name", "recordings", "uuid"]
        self.assertEqual(expected, sorted(data.keys()))

    def test_raag_detail_url(self):
        resp = self.apiclient.get("/api/hindustani/raag/3cecdb8e-2a54-4833-8049-b3d8060f7e32")
        self.assertEqual(200, resp.status_code)


class TaalTest(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.t = models.Taal.objects.create(
            name="taal", common_name="taal", uuid="4f55fa34-5f77-4570-888c-0596cfc8a81a"
        )

    def test_taal_by_id(self):
        good_id = self.t.id
        resp = self.apiclient.get(f"/api/hindustani/taal/{good_id}")
        self.assertRedirects(resp, "/api/hindustani/taal/4f55fa34-5f77-4570-888c-0596cfc8a81a", status_code=301)

        bad_id = good_id + 1
        resp = self.apiclient.get(f"/api/hindustani/taal/{bad_id}")
        self.assertEqual(404, resp.status_code)

    def test_render_taal_inner(self):
        s = api.TaalInnerSerializer(self.t)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        self.assertEqual(["common_name", "name", "uuid"], sorted(data.keys()))

    def test_render_taal_detail(self):
        s = api.TaalDetailSerializer(self.t)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        expected = ["aliases", "common_name", "composers", "name", "recordings", "uuid"]
        self.assertEqual(expected, sorted(data.keys()))

    def test_taal_detail_url(self):
        resp = self.apiclient.get("/api/hindustani/taal/4f55fa34-5f77-4570-888c-0596cfc8a81a")
        self.assertEqual(200, resp.status_code)


class FormTest(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.f = models.Form.objects.create(
            name="form", common_name="form", uuid="29847751-350b-4db2-9d18-630769ee2c6c"
        )

    def test_form_by_id(self):
        good_id = self.f.id
        resp = self.apiclient.get(f"/api/hindustani/form/{good_id}")
        self.assertRedirects(resp, "/api/hindustani/form/29847751-350b-4db2-9d18-630769ee2c6c", status_code=301)

        bad_id = good_id + 1
        resp = self.apiclient.get(f"/api/hindustani/form/{bad_id}")
        self.assertEqual(404, resp.status_code)

    def test_render_form_inner(self):
        s = api.FormInnerSerializer(self.f)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        self.assertEqual(["common_name", "name", "uuid"], sorted(data.keys()))

    def test_render_form_detail(self):
        s = api.FormDetailSerializer(self.f)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        expected = ["aliases", "artists", "common_name", "name", "recordings", "uuid"]
        self.assertEqual(expected, sorted(data.keys()))

    def test_taal_detail_url(self):
        resp = self.apiclient.get("/api/hindustani/form/29847751-350b-4db2-9d18-630769ee2c6c")
        self.assertEqual(200, resp.status_code)


class LayaTest(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.l = models.Laya.objects.create(
            name="laya", common_name="laya", uuid="e5d56b8c-f791-430a-ac2b-4c75f81a87c5"
        )

    def test_laya_by_id(self):
        good_id = self.l.id
        resp = self.apiclient.get(f"/api/hindustani/laya/{good_id}")
        self.assertRedirects(resp, "/api/hindustani/laya/e5d56b8c-f791-430a-ac2b-4c75f81a87c5", status_code=301)

        bad_id = good_id + 1
        resp = self.apiclient.get(f"/api/hindustani/laya/{bad_id}")
        self.assertEqual(404, resp.status_code)

    def test_render_laya_inner(self):
        s = api.LayaInnerSerializer(self.l)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        self.assertEqual(["common_name", "name", "uuid"], sorted(data.keys()))

    def test_render_laya_detail(self):
        s = api.LayaDetailSerializer(self.l)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        expected = ["aliases", "common_name", "name", "recordings", "uuid"]
        self.assertEqual(expected, sorted(data.keys()))

    def test_laya_detail_url(self):
        resp = self.apiclient.get("/api/hindustani/laya/e5d56b8c-f791-430a-ac2b-4c75f81a87c5")
        self.assertEqual(200, resp.status_code)


class ReleaseTest(ApiTestCase):
    def setUp(self):
        super().setUp()

        self.coll1id = str(uuid.uuid4())
        self.col1 = data.models.Collection.objects.create(
            collectionid=self.coll1id, name="collection 1", permission="U"
        )
        self.r = models.Release.objects.create(
            collection=self.col1, title="somerelease", mbid="c8296944-74f6-4277-94c9-9481d7a8ba81"
        )

        self.normaluser = auth.models.User.objects.create_user("normaluser")

        self.coll2id = str(uuid.uuid4())
        self.col2 = data.models.Collection.objects.create(
            collectionid=self.coll2id, name="collection 2", permission="S"
        )
        self.r = models.Release.objects.create(
            collection=self.col2, title="somerelease2", mbid="2c7638f6-d172-4dcd-bca7-06f912e0f09e"
        )

        self.coll3id = str(uuid.uuid4())
        self.col3 = data.models.Collection.objects.create(
            collectionid=self.coll3id, name="collection 3", permission="R"
        )
        self.r = models.Release.objects.create(
            collection=self.col3, title="somerelease3", mbid="b5c3a883-67f5-4d01-982f-6c70f3569191"
        )

    def test_release_list(self):
        """Staff members will see all the releases, but
        regular users only see those associated to
        unrestricted collections"""
        client = APIClient()
        client.force_authenticate(user=self.staffuser)

        collections = f"{self.coll1id}"
        response = client.get("/api/hindustani/release", **{"HTTP_DUNYA_COLLECTION": collections})

        data = response.data
        self.assertEqual(1, len(data["results"]))

        collections = f"{self.coll1id}, {self.coll2id}, {self.coll3id}"
        response = client.get("/api/hindustani/release", **{"HTTP_DUNYA_COLLECTION": collections})
        data = response.data

        self.assertEqual(3, len(data["results"]))

        # A normal user passing a restricted collection will still only
        # get 1 release
        client.force_authenticate(user=self.normaluser)
        collections = f"{self.coll1id}, {self.coll2id}"
        response = client.get("/api/hindustani/release", **{"HTTP_DUNYA_COLLECTION": collections})
        data = response.data
        self.assertEqual(1, len(data["results"]))

        # A restricted user passing a restricted collection will still only
        # get 2 release
        client.force_authenticate(user=self.restricteduser)
        collections = f"{self.coll1id}, {self.coll2id}, {self.coll3id}"
        response = client.get("/api/hindustani/release", **{"HTTP_DUNYA_COLLECTION": collections})
        data = response.data
        self.assertEqual(2, len(data["results"]))

    def test_render_release_inner(self):
        s = api.ReleaseInnerSerializer(self.r)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        self.assertEqual(["mbid", "title"], sorted(data.keys()))

    def test_render_release_detail(self):
        s = api.ReleaseDetailSerializer(self.r)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        expected = ["artists", "image", "mbid", "recordings", "release_artists", "title", "year"]
        self.assertEqual(expected, sorted(data.keys()))

    def test_laya_detail_url(self):
        resp = self.apiclient.get("/api/hindustani/release/c8296944-74f6-4277-94c9-9481d7a8ba81")
        self.assertEqual(200, resp.status_code)


class InstrumentTest(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.instmbid = str(uuid.uuid4())
        self.i = models.Instrument.objects.create(name="inst", id=9, mbid=self.instmbid)

    def test_render_instrument_inner(self):
        s = api.InstrumentInnerSerializer(self.i)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        self.assertEqual(["mbid", "name"], sorted(data.keys()))

    def test_render_instrument_detail(self):
        s = api.InstrumentDetailSerializer(self.i)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        expected = ["artists", "mbid", "name"]
        self.assertEqual(expected, sorted(data.keys()))

    def test_instrument_detail_url(self):
        resp = self.apiclient.get(f"/api/hindustani/instrument/{self.instmbid}")
        self.assertEqual(200, resp.status_code)
