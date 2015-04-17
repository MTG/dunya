from django.test import TestCase
from django.contrib import auth
from rest_framework.test import APIClient
from django.contrib.auth.models import Permission

import data
from carnatic import models
from carnatic import api

import uuid

class ArtistTest(TestCase):

    def setUp(self):
        permission = Permission.objects.get(codename='access_restricted')     
        self.a = models.Artist.objects.create(name="Foo", mbid="a484bcbc-c0d9-468a-952c-9938d5811f85")

        self.col1 = data.models.Collection.objects.create(name="collection 1", permission="U") 
        self.col1.save()
        self.cnormal = models.Concert.objects.create(title="normal concert", mbid="ef317442-1278-4349-8c52-29572fd3e937")
        self.cnormal.collection = self.col1
        self.cbootleg = models.Concert.objects.create(title="bootleg concert", mbid="cbe1ba35-8758-4a7d-9811-70bc48f41734", bootleg=True)
        self.cnormal.artists.add(self.a)
        self.cbootleg.artists.add(self.a)

        self.rnormal = models.Recording.objects.create(title="normal recording", mbid="dcf14452-e13e-450f-82c2-8ae705a58971")
        self.rbootleg = models.Recording.objects.create(title="bootleg recording", mbid="34275e18-0aef-4fa5-9618-b5938cb73a24")

        models.ConcertRecording.objects.create(concert=self.cnormal, recording=self.rnormal, track=1, disc=1, disctrack=1)
        models.ConcertRecording.objects.create(concert=self.cbootleg, recording=self.rbootleg, track=1, disc=1, disctrack=1)

        self.normaluser = auth.models.User.objects.create_user("normaluser")
        self.staffuser = auth.models.User.objects.create_user("staffuser")
        self.staffuser.is_staff = True
        self.staffuser.save()

    def test_render_artist_inner(self):
        s = api.ArtistInnerSerializer(self.a)
        expected = {"name": "Foo", "mbid": "a484bcbc-c0d9-468a-952c-9938d5811f85"}
        self.assertEquals(expected, s.data)

    def test_render_artist_detail(self):
        s = api.BootlegArtistDetailSerializer(self.a)
        keys = sorted(s.data.keys())
        self.assertEqual(["concerts", "instruments", "mbid", "name", "recordings"], keys)

    def test_artist_bootlegs_normal(self):
        client = APIClient()
        client.force_authenticate(user=self.normaluser)

        # With the normal user we only get the non-bootleg
        # concerts and recordings
        response = client.get("/api/carnatic/artist/a484bcbc-c0d9-468a-952c-9938d5811f85")
        data = response.data
        self.assertEqual(1, len(data["concerts"]))
        self.assertEqual("ef317442-1278-4349-8c52-29572fd3e937", data["concerts"][0]["mbid"])
        self.assertEqual(1, len(data["recordings"]))
        self.assertEqual("dcf14452-e13e-450f-82c2-8ae705a58971", data["recordings"][0]["mbid"])

        # Even if they ask for bootlegs, only the normal ones
        response = client.get("/api/carnatic/artist/a484bcbc-c0d9-468a-952c-9938d5811f85?with_bootlegs=True")
        data = response.data
        self.assertEqual(1, len(data["concerts"]))
        self.assertEqual(1, len(data["recordings"]))


    def test_artist_bootlegs_staff(self):
        # a staff user can choose if they see normal releases
        client = APIClient()
        client.force_authenticate(user=self.staffuser)
        response = client.get("/api/carnatic/artist/a484bcbc-c0d9-468a-952c-9938d5811f85")
        data = response.data
        self.assertEqual(1, len(data["concerts"]))
        self.assertEqual(1, len(data["recordings"]))

        # or bootlegs too
        response = client.get("/api/carnatic/artist/a484bcbc-c0d9-468a-952c-9938d5811f85?with_bootlegs=True")
        data = response.data
        self.assertEqual(2, len(data["concerts"]))
        self.assertEqual("ef317442-1278-4349-8c52-29572fd3e937", data["concerts"][0]["mbid"])
        self.assertEqual("cbe1ba35-8758-4a7d-9811-70bc48f41734", data["concerts"][1]["mbid"])
        self.assertEqual(2, len(data["recordings"]))
        recordings = sorted(data["recordings"], key=lambda x: x["mbid"])
        self.assertEqual("34275e18-0aef-4fa5-9618-b5938cb73a24", recordings[0]["mbid"])
        self.assertEqual("dcf14452-e13e-450f-82c2-8ae705a58971", recordings[1]["mbid"])

class ComposerTest(TestCase):
    def test_render_composer_inner(self):
        c = models.Composer.objects.create(name="Composer", mbid="")
        s = api.ComposerInnerSerializer(c)
        self.assertEquals(["mbid", "name"], sorted(s.data.keys()))

class RecordingTest(TestCase):
    def setUp(self):
        self.cnormal = models.Concert.objects.create(title="normal concert", mbid="ef317442-1278-4349-8c52-29572fd3e937")
        self.cbootleg = models.Concert.objects.create(title="bootleg concert", mbid="cbe1ba35-8758-4a7d-9811-70bc48f41734", bootleg=True)

        self.rnormal = models.Recording.objects.create(title="normal recording", mbid="dcf14452-e13e-450f-82c2-8ae705a58971")
        self.rbootleg = models.Recording.objects.create(title="bootleg recording", mbid="34275e18-0aef-4fa5-9618-b5938cb73a24")

        models.ConcertRecording.objects.create(concert=self.cnormal, recording=self.rnormal, track=1, disc=1, disctrack=1)
        models.ConcertRecording.objects.create(concert=self.cbootleg, recording=self.rbootleg, track=1, disc=1, disctrack=1)

        self.normaluser = auth.models.User.objects.create_user("normaluser")
        self.staffuser = auth.models.User.objects.create_user("staffuser")
        self.staffuser.is_staff = True
        self.staffuser.save()

    def test_render_recording_inner(self):
        s = api.RecordingInnerSerializer(self.rnormal)
        self.assertEquals(["mbid", "title"], sorted(s.data.keys()))

    def test_recording_list_bootleg(self):
        """ Staff members will see bootlegs recordings in
            this list too """
        client = APIClient()
        client.force_authenticate(user=self.staffuser)

        response = client.get("/api/carnatic/recording")
        data = response.data
        self.assertEqual(1, len(data["results"]))

        response = client.get("/api/carnatic/recording?with_bootlegs=True")
        data = response.data
        self.assertEqual(2, len(data["results"]))


        # A normal user using with_bootlegs=True will still only
        # get 1 recording
        client.force_authenticate(user=self.normaluser)
        response = client.get("/api/carnatic/recording?with_bootlegs=True")
        data = response.data
        self.assertEqual(1, len(data["results"]))

    def test_render_recording_detail(self):
        s = api.RecordingDetailSerializer(self.rnormal)
        fields = ['artists', 'concert', 'mbid', 'raaga', 'taala', 'title', 'work']
        self.assertEqual(fields, sorted(s.data.keys()))

    def test_recording_detail_bootleg(self):
        """ Only staff can access a bootleg recording """
        client = APIClient()
        client.force_authenticate(user=self.staffuser)

        response = client.get("/api/carnatic/recording/34275e18-0aef-4fa5-9618-b5938cb73a24")
        data = response.data
        self.assertEqual(200, response.status_code)
        fields = ['artists', 'concert', 'mbid', 'raaga', 'taala', 'title', 'work']
        self.assertEqual(fields, sorted(data.keys()))

        client.force_authenticate(user=self.normaluser)
        response = client.get("/api/carnatic/recording/34275e18-0aef-4fa5-9618-b5938cb73a24")
        self.assertEqual(404, response.status_code)

class WorkTest(TestCase):
    def setUp(self):
        self.cnormal = models.Concert.objects.create(title="normal concert", mbid="ef317442-1278-4349-8c52-29572fd3e937")
        self.cbootleg = models.Concert.objects.create(title="bootleg concert", mbid="cbe1ba35-8758-4a7d-9811-70bc48f41734", bootleg=True)

        self.wnormal = models.Work.objects.create(title="normal work", mbid="7ed898bc-fa11-41ae-b1c9-913d96c40e2b")
        self.wbootleg = models.Work.objects.create(title="bootleg work", mbid="b4e100b4-024f-4ed8-8942-9150e99d4c80")
        self.rnormal = models.Recording.objects.create(title="normal recording", mbid="dcf14452-e13e-450f-82c2-8ae705a58971", work=self.wnormal)
        self.rbootleg = models.Recording.objects.create(title="bootleg recording", mbid="34275e18-0aef-4fa5-9618-b5938cb73a24", work=self.wbootleg)

        models.ConcertRecording.objects.create(concert=self.cnormal, recording=self.rnormal, track=1, disc=1, disctrack=1)
        models.ConcertRecording.objects.create(concert=self.cbootleg, recording=self.rbootleg, track=1, disc=1, disctrack=1)

        self.normaluser = auth.models.User.objects.create_user("normaluser")
        self.staffuser = auth.models.User.objects.create_user("staffuser")
        self.staffuser.is_staff = True
        self.staffuser.save()

    def test_render_work_inner(self):
        w = models.Work(title="work", mbid="")
        s = api.WorkInnerSerializer(w)
        self.assertEquals(["mbid", "title"], sorted(s.data.keys()))

    def test_render_work_detail(self):
        w = models.Work.objects.create(title="work", mbid="")
        s = api.BootlegWorkDetailSerializer(w)
        fields = ['composers', 'mbid', 'raagas', 'recordings', 'taalas', 'title']
        self.assertEquals(fields, sorted(s.data.keys()))

    def test_work_bootleg_recordings_staff(self):
        client = APIClient()
        client.force_authenticate(user=self.staffuser)

        response = client.get("/api/carnatic/work/7ed898bc-fa11-41ae-b1c9-913d96c40e2b")
        data = response.data
        self.assertEqual(1, len(data["recordings"]))

        response = client.get("/api/carnatic/work/b4e100b4-024f-4ed8-8942-9150e99d4c80")
        data = response.data
        self.assertEqual(0, len(data["recordings"]))

        response = client.get("/api/carnatic/work/b4e100b4-024f-4ed8-8942-9150e99d4c80?with_bootlegs=True")
        data = response.data
        self.assertEqual(1, len(data["recordings"]))

    def test_work_bootleg_recordings_nostaff(self):
        client = APIClient()
        client.force_authenticate(user=self.normaluser)

        response = client.get("/api/carnatic/work/7ed898bc-fa11-41ae-b1c9-913d96c40e2b")
        data = response.data
        self.assertEqual(1, len(data["recordings"]))

        response = client.get("/api/carnatic/work/b4e100b4-024f-4ed8-8942-9150e99d4c80")
        data = response.data
        self.assertEqual(0, len(data["recordings"]))

        response = client.get("/api/carnatic/work/b4e100b4-024f-4ed8-8942-9150e99d4c80?with_bootlegs=True")
        data = response.data
        self.assertEqual(0, len(data["recordings"]))

class RaagaTest(TestCase):
    def setUp(self):
        self.raaga = models.Raaga.objects.create(id=1, name="My Raaga")

    def test_render_raaga_inner(self):
        s = api.RaagaInnerSerializer(self.raaga)
        self.assertEqual(["name", "uuid"], sorted(s.data.keys()))

        try:
            uuid.UUID(s.data["uuid"])
        except ValueError:
            self.fail("uuid is not correct/present")

    def test_render_raaga_detail(self):
        s = api.RaagaDetailSerializer(self.raaga)
        fields = ['aliases', 'artists', 'common_name', 'composers', 'name', 'uuid', 'works']
        self.assertEqual(fields, sorted(s.data.keys()))

class TaalaTest(TestCase):
    def setUp(self):
        self.taala = models.Taala.objects.create(id=1, name="My Taala")

    def test_render_taala_inner(self):
        s = api.TaalaInnerSerializer(self.taala)
        self.assertEqual(["name", "uuid"], sorted(s.data.keys()))

        try:
            uuid.UUID(s.data["uuid"])
        except ValueError:
            self.fail("uuid is not correct/present")

    def test_render_taala_detail(self):
        s = api.TaalaDetailSerializer(self.taala)
        fields = ['aliases', 'artists', 'common_name', 'composers', 'name', 'uuid', 'works']
        self.assertEqual(fields, sorted(s.data.keys()))

class ConcertTest(TestCase):
    def setUp(self):
        permission = Permission.objects.get(codename='access_restricted')     
        self.col1 = data.models.Collection.objects.create(name="collection 1", mbid="afd2", permission="U") 
        self.col1.save()
        self.cnormal = models.Concert.objects.create(title="normal concert", mbid="ef317442-1278-4349-8c52-29572fd3e937")
        self.cnormal.collection = self.col1
        self.cnormal.save()
        self.col2 = data.models.Collection.objects.create(mbid="afd3", name="collection 2", permission="S") 
        self.col2.save()
        self.cbootleg = models.Concert.objects.create(title="bootleg concert", mbid="cbe1ba35-8758-4a7d-9811-70bc48f41734", bootleg=True)
        self.cbootleg.collection = self.col2
        self.cbootleg.save()
        self.rnormal = models.Recording.objects.create(title="normal recording", mbid="34275e18-0aef-4fa5-9618-b5938cb73a24")
        models.ConcertRecording.objects.create(concert=self.cnormal, recording=self.rnormal, track=1, disc=1, disctrack=1)

        self.normaluser = auth.models.User.objects.create_user("normaluser")
        self.staffuser = auth.models.User.objects.create_user("staffuser")
        self.staffuser.is_staff = True
        self.staffuser.save()

    def test_render_concert_inner(self):
        s = api.ConcertInnerSerializer(self.cnormal)
        self.assertEqual(["mbid", "title"], sorted(s.data.keys()))

    def test_render_concert_detail(self):
        s = api.ConcertDetailSerializer(self.cnormal)
        fields = ['artists', 'concert_artists', 'image', 'mbid','recordings', 'title', 'year']
        self.assertEqual(fields, sorted(s.data.keys()))

        recordings = s.data["recordings"]
        self.assertEqual(1, len(recordings))
        r = recordings[0]
        expected = {"title": "normal recording", "mbid": "34275e18-0aef-4fa5-9618-b5938cb73a24", "disc": 1, "track": 1, "disctrack": 1}
        self.assertEqual(expected, r)

    def test_concert_list_bootleg(self):
        """ Staff members will see bootleg concerts in
            this list if they ask for them """
        client = APIClient()
        client.force_authenticate(user=self.staffuser)

        response = client.get("/api/carnatic/concert", **{'HTTP_DUNYA_COLLECTION':'afd2'})

        data = response.data
        self.assertEqual(1, len(data["results"]))

        response = client.get("/api/carnatic/concert?with_bootlegs=True", **{'HTTP_DUNYA_COLLECTION':'afd2, afd3'})
        data = response.data
        
        self.assertEqual(2, len(data["results"]))


        # A normal user using with_bootlegs=True will still only
        # get 1 concert
        client.force_authenticate(user=self.normaluser)
        response = client.get("/api/carnatic/concert?with_bootlegs=True", **{'HTTP_DUNYA_COLLECTION':'afd2, afd3'})
        data = response.data
        self.assertEqual(1, len(data["results"]))

    def test_concert_detail_bootleg(self):
        """ Only staff can access a bootleg concert """
        client = APIClient()
        client.force_authenticate(user=self.staffuser)

        response = client.get("/api/carnatic/concert/cbe1ba35-8758-4a7d-9811-70bc48f41734")
        data = response.data
        self.assertEqual(200, response.status_code)

        client.force_authenticate(user=self.normaluser)
        response = client.get("/api/carnatic/concert/cbe1ba35-8758-4a7d-9811-70bc48f41734")
        self.assertEqual(404, response.status_code)


class InstrumentTest(TestCase):
    def setUp(self):
        self.inst = models.Instrument.objects.create(id=1, name="My Taala")

    def test_render_instrument_inner(self):
        s = api.InstrumentInnerSerializer(self.inst)
        self.assertEqual(["id", "name"], sorted(s.data.keys()))

    def test_render_instrument_detail(self):
        s = api.InstrumentDetailSerializer(self.inst)
        fields = ['artists', 'id', 'name']
        self.assertEqual(fields, sorted(s.data.keys()))
