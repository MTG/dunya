import json
import uuid

from django.contrib import auth
from django.contrib.auth.models import Permission
from django.test import TestCase
from rest_framework.renderers import JSONRenderer
from rest_framework.test import APIClient

import data
from carnatic import api
from carnatic import models


class ArtistTest(TestCase):

    def setUp(self):
        self.a = models.Artist.objects.create(name="Foo", mbid="a484bcbc-c0d9-468a-952c-9938d5811f85")
        self.coll1id = str(uuid.uuid4())
        self.col1 = data.models.Collection.objects.create(collectionid=self.coll1id, name="collection 1",
                                                          permission="U")

        self.cnormal = models.Concert.objects.create(collection=self.col1, title="normal concert",
                                                     mbid="ef317442-1278-4349-8c52-29572fd3e937")
        self.coll2id = str(uuid.uuid4())
        self.col2 = data.models.Collection.objects.create(collectionid=self.coll2id, name="collection 2",
                                                          permission="R")
        self.crestricted = models.Concert.objects.create(collection=self.col2, title="restricted concert",
                                                         mbid="663cbe20-e8e1-11e4-9964-0002a5d5c51b")

        self.coll3id = str(uuid.uuid4())
        self.col3 = data.models.Collection.objects.create(collectionid=self.coll3id, name="collection 3",
                                                          permission="S")
        self.cstaff = models.Concert.objects.create(collection=self.col3, title="staff concert",
                                                    mbid="cbe1ba35-8758-4a7d-9811-70bc48f41734")

        self.cnormal.artists.add(self.a)
        self.cstaff.artists.add(self.a)
        self.crestricted.artists.add(self.a)

        self.rnormal = models.Recording.objects.create(title="normal recording",
                                                       mbid="dcf14452-e13e-450f-82c2-8ae705a58971")
        self.rrestricted = models.Recording.objects.create(title="restricted recording",
                                                           mbid="b287fe20-e8e1-11e4-bf83-0002a5d5c51b")
        self.rstaff = models.Recording.objects.create(title="staff recording",
                                                      mbid="34275e18-0aef-4fa5-9618-b5938cb73a24")

        models.ConcertRecording.objects.create(concert=self.cnormal, recording=self.rnormal, track=1, disc=1,
                                               disctrack=1)
        models.ConcertRecording.objects.create(concert=self.crestricted, recording=self.rrestricted, track=1, disc=1,
                                               disctrack=1)
        models.ConcertRecording.objects.create(concert=self.cstaff, recording=self.rstaff, track=1, disc=1, disctrack=1)

        permission = Permission.objects.get(codename='access_restricted')
        self.normaluser = auth.models.User.objects.create_user("normaluser")
        self.restricteduser = auth.models.User.objects.create_user("restricteduser")
        self.restricteduser.user_permissions.add(permission)
        self.restricteduser.save()
        self.staffuser = auth.models.User.objects.create_user("staffuser")
        self.staffuser.is_staff = True
        self.staffuser.save()

    def test_render_artist_inner(self):
        s = api.ArtistInnerSerializer(self.a)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        expected = {"name": "Foo", "mbid": "a484bcbc-c0d9-468a-952c-9938d5811f85"}
        self.assertEqual(expected, data)

    def test_render_artist_detail(self):
        client = APIClient()
        client.force_authenticate(user=self.normaluser)

        response = client.get("/api/carnatic/artist/a484bcbc-c0d9-468a-952c-9938d5811f85")
        data = response.data

        keys = sorted(data.keys())
        self.assertEqual(["concerts", "instruments", "mbid", "name", "recordings"], keys)

    def test_artist_normal_collection(self):
        client = APIClient()
        client.force_authenticate(user=self.normaluser)

        # With the normal user we only get the unrestricted collection's
        # concerts and recordings
        collections = self.coll1id
        response = client.get("/api/carnatic/artist/a484bcbc-c0d9-468a-952c-9938d5811f85",
                              **{'HTTP_DUNYA_COLLECTION': collections})
        data = response.data
        self.assertEqual(1, len(data["concerts"]))
        self.assertEqual("ef317442-1278-4349-8c52-29572fd3e937", data["concerts"][0]["mbid"])
        self.assertEqual(1, len(data["recordings"]))
        self.assertEqual("dcf14452-e13e-450f-82c2-8ae705a58971", data["recordings"][0]["mbid"])

        # Even if they ask for restricted collection, only the normal ones
        collections = self.coll1id
        response = client.get("/api/carnatic/artist/a484bcbc-c0d9-468a-952c-9938d5811f85",
                              **{'HTTP_DUNYA_COLLECTION': collections})
        data = response.data
        self.assertEqual(1, len(data["concerts"]))
        self.assertEqual(1, len(data["recordings"]))

    def test_artist_invalid_collection(self):
        # An invalid uuid is passed in the Dunya-Collection header
        client = APIClient()
        client.force_authenticate(user=self.normaluser)

        # With the normal user we only get the unrestricted collection's
        # concerts and recordings
        response = client.get("/api/carnatic/artist/a484bcbc-c0d9-468a-952c-9938d5811f85",
                              **{'HTTP_DUNYA_COLLECTION': 'not-uuid'})
        self.assertEquals(response.status_code, 400)

    def test_artist_collections_staff(self):
        # a staff user can choose if they see normal releases
        client = APIClient()
        client.force_authenticate(user=self.staffuser)
        collections = self.coll1id
        response = client.get("/api/carnatic/artist/a484bcbc-c0d9-468a-952c-9938d5811f85",
                              **{'HTTP_DUNYA_COLLECTION': collections})
        data = response.data
        self.assertEqual(1, len(data["concerts"]))
        self.assertEqual(1, len(data["recordings"]))

        # or restricted collections too
        collections = "%s, %s" % (self.coll1id, self.coll3id)
        response = client.get("/api/carnatic/artist/a484bcbc-c0d9-468a-952c-9938d5811f85",
                              **{'HTTP_DUNYA_COLLECTION': collections})
        data = response.data
        self.assertEqual(2, len(data["concerts"]))
        self.assertEqual("ef317442-1278-4349-8c52-29572fd3e937", data["concerts"][0]["mbid"])
        self.assertEqual("cbe1ba35-8758-4a7d-9811-70bc48f41734", data["concerts"][1]["mbid"])
        self.assertEqual(2, len(data["recordings"]))
        recordings = sorted(data["recordings"], key=lambda x: x["mbid"])
        self.assertEqual("34275e18-0aef-4fa5-9618-b5938cb73a24", recordings[0]["mbid"])
        self.assertEqual("dcf14452-e13e-450f-82c2-8ae705a58971", recordings[1]["mbid"])

    def test_artist_collections_restricted(self):
        # a restricted user can choose if they see normal releases
        client = APIClient()
        client.force_authenticate(user=self.restricteduser)
        collections = self.coll1id
        response = client.get("/api/carnatic/artist/a484bcbc-c0d9-468a-952c-9938d5811f85",
                              **{'HTTP_DUNYA_COLLECTION': collections})
        data = response.data
        self.assertEqual(1, len(data["concerts"]))
        self.assertEqual(1, len(data["recordings"]))

        # or restricted collections too
        collections = "%s, %s" % (self.coll1id, self.coll2id)
        response = client.get("/api/carnatic/artist/a484bcbc-c0d9-468a-952c-9938d5811f85",
                              **{'HTTP_DUNYA_COLLECTION': collections})
        data = response.data
        self.assertEqual(2, len(data["concerts"]))
        self.assertEqual("ef317442-1278-4349-8c52-29572fd3e937", data["concerts"][0]["mbid"])
        self.assertEqual("663cbe20-e8e1-11e4-9964-0002a5d5c51b", data["concerts"][1]["mbid"])
        self.assertEqual(2, len(data["recordings"]))
        recordings = sorted(data["recordings"], key=lambda x: x["mbid"])
        self.assertEqual("b287fe20-e8e1-11e4-bf83-0002a5d5c51b", recordings[0]["mbid"])
        self.assertEqual("dcf14452-e13e-450f-82c2-8ae705a58971", recordings[1]["mbid"])


class ComposerTest(TestCase):
    def test_render_composer_inner(self):
        mbid = uuid.uuid4()
        c = models.Composer.objects.create(name="Composer", mbid=mbid)
        s = api.ComposerInnerSerializer(c)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        self.assertEqual(["mbid", "name"], sorted(data.keys()))


class RecordingTest(TestCase):
    def setUp(self):
        self.coll1id = str(uuid.uuid4())
        self.col1 = data.models.Collection.objects.create(collectionid=self.coll1id, name="collection 1",
                                                          permission="U")
        self.cnormal = models.Concert.objects.create(collection=self.col1, title="normal concert",
                                                     mbid="ef317442-1278-4349-8c52-29572fd3e937")

        self.coll2id = str(uuid.uuid4())
        self.col2 = data.models.Collection.objects.create(collectionid=self.coll2id, name="collection 2",
                                                          permission="R")
        self.crestricted = models.Concert.objects.create(collection=self.col2, title="restricted concert",
                                                         mbid="cbe1ba35-8758-4a7d-9811-70bc48f41734")

        self.coll3id = str(uuid.uuid4())
        self.col3 = data.models.Collection.objects.create(collectionid=self.coll3id, name="collection 3",
                                                          permission="S")
        self.cstaff = models.Concert.objects.create(collection=self.col3, title="staff concert",
                                                    mbid="663cbe20-e8e1-11e4-9964-0002a5d5c51b")

        self.wnormal = models.Work.objects.create(title="normal work", mbid="7ed898bc-fa11-41ae-b1c9-913d96c40e2b")
        self.wrestricted = models.Work.objects.create(title="restricted work",
                                                      mbid="b4e100b4-024f-4ed8-8942-9150e99d4c80")
        self.rnormal = models.Recording.objects.create(title="normal recording",
                                                       mbid="dcf14452-e13e-450f-82c2-8ae705a58971")
        models.RecordingWork.objects.create(recording=self.rnormal, work=self.wnormal, sequence=1)
        self.rrestricted = models.Recording.objects.create(title="restricted recording",
                                                           mbid="34275e18-0aef-4fa5-9618-b5938cb73a24")
        models.RecordingWork.objects.create(recording=self.rrestricted, work=self.wrestricted, sequence=1)
        self.wstaff = models.Work.objects.create(title="staff work", mbid="91e8db80-e8e1-11e4-a224-0002a5d5c51b")
        self.rstaff = models.Recording.objects.create(title="staff recording",
                                                      mbid="b287fe20-e8e1-11e4-bf83-0002a5d5c51b")
        models.RecordingWork.objects.create(recording=self.rstaff, work=self.wstaff, sequence=1)

        models.ConcertRecording.objects.create(concert=self.cnormal, recording=self.rnormal, track=1, disc=1,
                                               disctrack=1)
        models.ConcertRecording.objects.create(concert=self.crestricted, recording=self.rrestricted, track=1, disc=1,
                                               disctrack=1)
        models.ConcertRecording.objects.create(concert=self.cstaff, recording=self.rstaff, track=1, disc=1, disctrack=1)

        permission = Permission.objects.get(codename='access_restricted')
        self.normaluser = auth.models.User.objects.create_user("normaluser")
        self.restricteduser = auth.models.User.objects.create_user("restricteduser")
        self.restricteduser.user_permissions.add(permission)
        self.restricteduser.save()
        self.staffuser = auth.models.User.objects.create_user("staffuser")
        self.staffuser.is_staff = True
        self.staffuser.save()

    def test_render_recording_inner(self):
        s = api.RecordingInnerSerializer(self.rnormal)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        self.assertEqual(["mbid", "title"], sorted(data.keys()))

    def test_recording_list_collection(self):
        """ Staff members will see recordings from restricted collections in
            this list too """
        client = APIClient()
        client.force_authenticate(user=self.staffuser)

        collections = self.coll3id
        response = client.get("/api/carnatic/recording", **{'HTTP_DUNYA_COLLECTION': collections})
        data = response.data
        self.assertEqual(1, len(data["results"]))
        response = client.get("/api/carnatic/recording")
        data = response.data
        self.assertEqual(3, len(data["results"]))

        # A restricted user passing a restricted collection over the header parameter will
        # get 1 recording
        client.force_authenticate(user=self.restricteduser)

        collections = self.coll2id
        response = client.get("/api/carnatic/recording", **{'HTTP_DUNYA_COLLECTION': collections})
        data = response.data
        self.assertEqual(1, len(data["results"]))

        # A normal user passing a collection over the header parameter will still only
        # get 1 recording
        client.force_authenticate(user=self.normaluser)
        collections = self.coll1id
        response = client.get("/api/carnatic/recording", **{'HTTP_DUNYA_COLLECTION': collections})
        data = response.data
        self.assertEqual(1, len(data["results"]))

    def test_render_recording_detail(self):
        client = APIClient()
        client.force_authenticate(user=self.staffuser)

        response = client.get("/api/carnatic/recording/34275e18-0aef-4fa5-9618-b5938cb73a24")
        data = response.data
        fields = ['album_artists', 'artists', 'concert', 'form', 'length', 'mbid', 'raaga', 'taala', 'title', 'work']
        self.assertEqual(fields, sorted(data.keys()))

    def test_recording_detail_restr_collection(self):
        """ Only staff can access a recording from restricted collections"""
        client = APIClient()
        client.force_authenticate(user=self.staffuser)

        response = client.get("/api/carnatic/recording/34275e18-0aef-4fa5-9618-b5938cb73a24")
        data = response.data
        self.assertEqual(200, response.status_code)
        fields = ['album_artists', 'artists', 'concert', 'form', 'length', 'mbid', 'raaga', 'taala', 'title', 'work']
        self.assertEqual(fields, sorted(data.keys()))

        # If we request another collection over the header parameter
        # we get a 404
        client.force_authenticate(user=self.normaluser)
        response = client.get("/api/carnatic/recording/34275e18-0aef-4fa5-9618-b5938cb73a24",
                              **{'HTTP_DUNYA_COLLECTION': str(uuid.uuid4())})
        self.assertEqual(404, response.status_code)


class WorkTest(TestCase):
    def setUp(self):
        self.coll1id = str(uuid.uuid4())
        self.col1 = data.models.Collection.objects.create(collectionid=self.coll1id, name="collection 1",
                                                          permission="U")

        self.cnormal = models.Concert.objects.create(collection=self.col1, title="normal concert",
                                                     mbid="ef317442-1278-4349-8c52-29572fd3e937")
        self.coll2id = str(uuid.uuid4())
        self.col2 = data.models.Collection.objects.create(collectionid=self.coll2id, name="collection 2",
                                                          permission="R")
        self.crestricted = models.Concert.objects.create(collection=self.col2, title="restricted concert",
                                                         mbid="cbe1ba35-8758-4a7d-9811-70bc48f41734")

        self.coll3id = str(uuid.uuid4())
        self.col3 = data.models.Collection.objects.create(collectionid=self.coll3id, name="collection 3",
                                                          permission="S")
        self.cstaff = models.Concert.objects.create(collection=self.col3, title="staff concert",
                                                    mbid="663cbe20-e8e1-11e4-9964-0002a5d5c51b")

        self.wnormal = models.Work.objects.create(title="normal work", mbid="7ed898bc-fa11-41ae-b1c9-913d96c40e2b")
        self.wrestricted = models.Work.objects.create(title="restricted work",
                                                      mbid="b4e100b4-024f-4ed8-8942-9150e99d4c80")
        self.rnormal = models.Recording.objects.create(title="normal recording",
                                                       mbid="dcf14452-e13e-450f-82c2-8ae705a58971")
        models.RecordingWork.objects.create(recording=self.rnormal, work=self.wnormal, sequence=1)
        self.rrestricted = models.Recording.objects.create(title="restricted recording",
                                                           mbid="34275e18-0aef-4fa5-9618-b5938cb73a24")
        models.RecordingWork.objects.create(recording=self.rrestricted, work=self.wrestricted, sequence=1)
        self.wstaff = models.Work.objects.create(title="staff work", mbid="91e8db80-e8e1-11e4-a224-0002a5d5c51b")
        self.rstaff = models.Recording.objects.create(title="staff recording",
                                                      mbid="b287fe20-e8e1-11e4-bf83-0002a5d5c51b")
        models.RecordingWork.objects.create(recording=self.rstaff, work=self.wstaff, sequence=1)

        models.ConcertRecording.objects.create(concert=self.cnormal, recording=self.rnormal, track=1, disc=1,
                                               disctrack=1)
        models.ConcertRecording.objects.create(concert=self.crestricted, recording=self.rrestricted, track=1, disc=1,
                                               disctrack=1)
        models.ConcertRecording.objects.create(concert=self.cstaff, recording=self.rstaff, track=1, disc=1, disctrack=1)

        permission = Permission.objects.get(codename='access_restricted')
        self.normaluser = auth.models.User.objects.create_user("normaluser")
        self.restricteduser = auth.models.User.objects.create_user("restricteduser")
        self.restricteduser.user_permissions.add(permission)
        self.restricteduser.save()
        self.staffuser = auth.models.User.objects.create_user("staffuser")
        self.staffuser.is_staff = True
        self.staffuser.save()

    def test_render_work_inner(self):
        w = models.Work(title="work", mbid="")
        s = api.WorkInnerSerializer(w)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        self.assertEqual(["mbid", "title"], sorted(data.keys()))

    def test_render_work_detail(self):
        client = APIClient()
        client.force_authenticate(user=self.staffuser)

        response = client.get("/api/carnatic/work/7ed898bc-fa11-41ae-b1c9-913d96c40e2b")
        data = response.data
        fields = ['composers', 'lyricists', 'mbid', 'raagas', 'recordings', 'taalas', 'title']
        self.assertEqual(fields, sorted(data.keys()))

    def test_work_collection_recordings_staff(self):
        client = APIClient()
        client.force_authenticate(user=self.staffuser)

        collections = self.coll1id
        response = client.get("/api/carnatic/work/7ed898bc-fa11-41ae-b1c9-913d96c40e2b",
                              **{'HTTP_DUNYA_COLLECTION': collections})
        data = response.data
        self.assertEqual(1, len(data["recordings"]))

        # unknown id
        collections = str(uuid.uuid4())
        response = client.get("/api/carnatic/work/b4e100b4-024f-4ed8-8942-9150e99d4c80",
                              **{'HTTP_DUNYA_COLLECTION': collections})
        data = response.data
        self.assertEqual(0, len(data["recordings"]))

        collections = "%s, %s" % (self.coll1id, self.coll2id)
        response = client.get("/api/carnatic/work/b4e100b4-024f-4ed8-8942-9150e99d4c80",
                              **{'HTTP_DUNYA_COLLECTION': collections})
        data = response.data
        self.assertEqual(1, len(data["recordings"]))

    def test_work_collection_recordings_restricted(self):
        client = APIClient()
        client.force_authenticate(user=self.restricteduser)

        collections = self.coll1id
        response = client.get("/api/carnatic/work/7ed898bc-fa11-41ae-b1c9-913d96c40e2b",
                              **{'HTTP_DUNYA_COLLECTION': collections})
        data = response.data
        self.assertEqual(1, len(data["recordings"]))

        collections = self.coll3id
        response = client.get("/api/carnatic/work/b4e100b4-024f-4ed8-8942-9150e99d4c80",
                              **{'HTTP_DUNYA_COLLECTION': collections})
        data = response.data
        self.assertEqual(0, len(data["recordings"]))

        collections = self.coll2id
        response = client.get("/api/carnatic/work/b4e100b4-024f-4ed8-8942-9150e99d4c80",
                              **{'HTTP_DUNYA_COLLECTION': collections})
        data = response.data
        self.assertEqual(1, len(data["recordings"]))

    def test_work_collection_recordings_nostaff(self):
        client = APIClient()
        client.force_authenticate(user=self.normaluser)

        collections = self.coll1id
        response = client.get("/api/carnatic/work/7ed898bc-fa11-41ae-b1c9-913d96c40e2b",
                              **{'HTTP_DUNYA_COLLECTION': collections})
        data = response.data
        self.assertEqual(1, len(data["recordings"]))

        response = client.get("/api/carnatic/work/b4e100b4-024f-4ed8-8942-9150e99d4c80")
        data = response.data
        self.assertEqual(0, len(data["recordings"]))

        collections = "%s, %s, %s" % (self.coll1id, self.coll3id, self.coll2id)
        response = client.get("/api/carnatic/work/b4e100b4-024f-4ed8-8942-9150e99d4c80",
                              **{'HTTP_DUNYA_COLLECTION': collections})
        data = response.data
        self.assertEqual(0, len(data["recordings"]))


class RaagaTest(TestCase):
    def setUp(self):
        self.raaga = models.Raaga.objects.create(id=1, name="My Raaga", uuid='d5285bf4-c3c5-454e-a659-fec30075990b')
        self.normaluser = auth.models.User.objects.create_user("normaluser")
        self.form = models.Form.objects.create(attrfromrecording=True, name='form')

        self.recording = models.Recording.objects.create(title="recording", mbid="34275e18-0aef-4fa5-9618-b5938cb73a24")
        models.RecordingRaaga.objects.create(raaga=self.raaga, recording=self.recording)
        models.RecordingForm.objects.create(sequence=1, form=self.form, recording=self.recording)

        self.form2 = models.Form.objects.create(attrfromrecording=False, name='form')
        self.work = models.Work.objects.create(title="normal work", mbid="7ed898bc-fa11-41ae-b1c9-913d96c40e2b",
                                               raaga=self.raaga)
        self.recording2 = models.Recording.objects.create(title="recording2",
                                                          mbid="44275e18-0aef-4fa5-9618-b5938cb73a24")
        models.RecordingForm.objects.create(sequence=1, form=self.form2, recording=self.recording2)
        models.RecordingWork.objects.create(recording=self.recording2, work=self.work, sequence=1)

    def test_render_raaga_inner(self):
        s = api.RaagaInnerSerializer(self.raaga)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        self.assertEqual(["common_name", "name", "uuid"], sorted(data.keys()))

        try:
            uuid.UUID(data["uuid"])
        except ValueError:
            self.fail("uuid is not correct/present")

    def test_render_raaga_detail(self):
        client = APIClient()
        client.force_authenticate(user=self.normaluser)
        response = client.get("/api/carnatic/raaga/d5285bf4-c3c5-454e-a659-fec30075990b")
        data = response.data
        fields = ['aliases', 'artists', 'common_name', 'composers', 'name', 'recordings', 'uuid', 'works']
        self.assertEqual(fields, sorted(data.keys()))

    def test_recording_raaga(self):
        client = APIClient()
        client.force_authenticate(user=self.normaluser)
        response = client.get("/api/carnatic/raaga/d5285bf4-c3c5-454e-a659-fec30075990b")

        data = response.data
        # For now we return the Recordings that are directly related
        # and the recordings that are related with a work with this raaga
        self.assertEqual(2, len(data["recordings"]))

        # Test get_raaga method from recording
        data = self.recording.get_raaga()
        self.assertEqual(1, len(data))

        data = self.recording2.get_raaga()
        self.assertEqual(1, len(data))


class TaalaTest(TestCase):
    def setUp(self):
        self.taala = models.Taala.objects.create(id=1, name="My Taala", uuid='d5285bf4-c3c5-454e-a659-fec30075990b')
        self.normaluser = auth.models.User.objects.create_user("normaluser")
        self.form = models.Form.objects.create(attrfromrecording=True, name='form')

        self.recording = models.Recording.objects.create(title="recording", mbid="34275e18-0aef-4fa5-9618-b5938cb73a24")
        models.RecordingTaala.objects.create(taala=self.taala, recording=self.recording)
        models.RecordingForm.objects.create(sequence=1, form=self.form, recording=self.recording)

        self.form2 = models.Form.objects.create(attrfromrecording=False, name='form')
        self.work = models.Work.objects.create(title="normal work", mbid="7ed898bc-fa11-41ae-b1c9-913d96c40e2b",
                                               taala=self.taala)
        self.recording2 = models.Recording.objects.create(title="recording2",
                                                          mbid="44275e18-0aef-4fa5-9618-b5938cb73a24")
        models.RecordingForm.objects.create(sequence=1, form=self.form2, recording=self.recording2)

        models.RecordingWork.objects.create(recording=self.recording2, work=self.work, sequence=1)

    def test_render_taala_inner(self):
        s = api.TaalaInnerSerializer(self.taala)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        self.assertEqual(["common_name", "name", "uuid"], sorted(data.keys()))

        try:
            uuid.UUID(data["uuid"])
        except ValueError:
            self.fail("uuid is not correct/present")

    def test_render_taala_detail(self):
        client = APIClient()
        client.force_authenticate(user=self.normaluser)
        response = client.get("/api/carnatic/taala/d5285bf4-c3c5-454e-a659-fec30075990b")
        data = response.data
        fields = ['aliases', 'artists', 'common_name', 'composers', 'name', 'recordings', 'uuid', 'works']
        self.assertEqual(fields, sorted(data.keys()))

    def test_recording_taala(self):
        client = APIClient()
        client.force_authenticate(user=self.normaluser)
        response = client.get("/api/carnatic/taala/d5285bf4-c3c5-454e-a659-fec30075990b")

        data = response.data
        self.assertEqual(1, len(data["recordings"]))

        # Test get_taala method from recording
        data = self.recording.get_taala()
        self.assertEqual(1, len(data))

        data = self.recording2.get_taala()
        self.assertEqual(1, len(data))


class ConcertTest(TestCase):
    def setUp(self):
        permission = Permission.objects.get(codename='access_restricted')
        self.coll1id = str(uuid.uuid4())
        self.col1 = data.models.Collection.objects.create(name="collection 1", collectionid=self.coll1id,
                                                          permission="U")
        self.cnormal = models.Concert.objects.create(title="normal concert",
                                                     mbid="ef317442-1278-4349-8c52-29572fd3e937")
        self.cnormal.collection = self.col1
        self.cnormal.save()
        self.coll2id = str(uuid.uuid4())
        self.col2 = data.models.Collection.objects.create(collectionid=self.coll2id, name="collection 2",
                                                          permission="S")
        self.col2.save()
        self.cbootleg = models.Concert.objects.create(title="bootleg concert",
                                                      mbid="cbe1ba35-8758-4a7d-9811-70bc48f41734")
        self.cbootleg.collection = self.col2
        self.cbootleg.save()
        self.rnormal = models.Recording.objects.create(title="normal recording",
                                                       mbid="34275e18-0aef-4fa5-9618-b5938cb73a24")
        models.ConcertRecording.objects.create(concert=self.cnormal, recording=self.rnormal, track=1, disc=1,
                                               disctrack=1)

        self.coll3id = str(uuid.uuid4())
        self.col3 = data.models.Collection.objects.create(collectionid=self.coll3id, name="collection 3",
                                                          permission="R")
        self.restricted = models.Concert.objects.create(collection=self.col3, title="restricted concert",
                                                        mbid="abe1ba35-8758-4a7d-9811-70bc48f41734")

        self.normaluser = auth.models.User.objects.create_user("normaluser")
        self.restricteduser = auth.models.User.objects.create_user("restricteduser")
        self.restricteduser.user_permissions.add(permission)
        self.restricteduser.save()
        self.restricteduser = auth.models.User.objects.get(pk=self.restricteduser.id)
        self.staffuser = auth.models.User.objects.create_user("staffuser")
        self.staffuser.is_staff = True
        self.staffuser.save()

    def test_render_concert_inner(self):
        s = api.ConcertInnerSerializer(self.cnormal)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        self.assertEqual(["mbid", "title"], sorted(data.keys()))

    def test_render_concert_detail(self):
        s = api.ConcertDetailSerializer(self.cnormal)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        fields = ['artists', 'concert_artists', 'image', 'mbid', 'recordings', 'title', 'year']
        self.assertEqual(fields, sorted(data.keys()))

        recordings = data["recordings"]
        self.assertEqual(1, len(recordings))
        r = recordings[0]
        expected = {"title": "normal recording", "mbid": "34275e18-0aef-4fa5-9618-b5938cb73a24", "disc": 1, "track": 1,
                    "disctrack": 1}
        self.assertEqual(expected, r)

    def test_concert_list_collection(self):
        """ Staff members will see concerts from restricted collections in
            this list if they ask for them """
        client = APIClient()
        client.force_authenticate(user=self.staffuser)

        collections = self.coll1id
        response = client.get("/api/carnatic/concert", **{'HTTP_DUNYA_COLLECTION': collections})

        data = response.data
        self.assertEqual(1, len(data["results"]))

        collections = "%s, %s" % (self.coll1id, self.coll2id)
        response = client.get("/api/carnatic/concert", **{'HTTP_DUNYA_COLLECTION': collections})
        data = response.data

        self.assertEqual(2, len(data["results"]))

        # A normal user passing a collection over header parameter will still only
        # get 1 concert
        client.force_authenticate(user=self.normaluser)
        collections = "%s, %s" % (self.coll1id, self.coll2id)
        response = client.get("/api/carnatic/concert", **{'HTTP_DUNYA_COLLECTION': collections})
        data = response.data
        self.assertEqual(1, len(data["results"]))

        # A restricted user using will get the concert associated
        # with the restricted access collection
        client.force_authenticate(user=self.restricteduser)
        collections = "%s, %s, %s" % (self.coll1id, self.coll2id, self.coll3id)
        response = client.get("/api/carnatic/concert", **{'HTTP_DUNYA_COLLECTION': collections})
        data = response.data
        self.assertEqual(2, len(data["results"]))

    def test_concert_detail_collection(self):
        """ Only staff can access a concert from a restricted collection"""
        client = APIClient()
        client.force_authenticate(user=self.staffuser)

        response = client.get("/api/carnatic/concert/cbe1ba35-8758-4a7d-9811-70bc48f41734")
        self.assertEqual(200, response.status_code)

        client.force_authenticate(user=self.normaluser)
        response = client.get("/api/carnatic/concert/cbe1ba35-8758-4a7d-9811-70bc48f41734")
        self.assertEqual(404, response.status_code)


class InstrumentTest(TestCase):
    def setUp(self):
        self.inst = models.Instrument.objects.create(id=1, name="My Taala")

    def test_render_instrument_inner(self):
        s = api.InstrumentInnerSerializer(self.inst)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        self.assertEqual(["mbid", "name"], sorted(data.keys()))

    def test_render_instrument_detail(self):
        s = api.InstrumentDetailSerializer(self.inst)
        data = json.loads(JSONRenderer().render(s.data).decode("utf-8"))
        fields = ['artists', 'mbid', 'name']
        self.assertEqual(fields, sorted(data.keys()))
