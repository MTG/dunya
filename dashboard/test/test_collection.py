from unittest import mock

import requests
from django.contrib import auth
from django.http import QueryDict
from django.test import TestCase

import docserver
from dashboard import forms, models, views


class CollectionTest(TestCase):
    """Test creation and view of new Collections"""

    def setUp(self):
        self.user1 = auth.models.User.objects.create_user("user1", "")
        self.user1.is_staff = True
        self.user1.save()

        self.mockname = mock.Mock(return_value="My collection")
        forms.compmusic.musicbrainz.get_collection_name = self.mockname
        self.pathmock = mock.Mock(return_value=True)
        forms.os.path.exists = self.pathmock

    def test_valid_form(self):
        formdata = "collectionid=55412ad8-1b15-44d5-8dc8-9c3cb0cf9e5d&path=%2Fsome%2Fpath"
        data = QueryDict(formdata)
        f = forms.AddCollectionForm(data)

        self.assertTrue(f.is_valid())
        self.assertEqual("My collection", f.cleaned_data["collectionname"])
        self.mockname.assert_called_once_with("55412ad8-1b15-44d5-8dc8-9c3cb0cf9e5d")
        calls = [mock.call("/some/path"), mock.call("/some/path/audio")]
        self.pathmock.assert_has_calls(calls)

    def test_no_path(self):
        pathmock = mock.Mock(return_value=False)
        forms.os.path.exists = pathmock

        formdata = "collectionid=55412ad8-1b15-44d5-8dc8-9c3cb0cf9e5d&path=%2Fsome%2Fpath"
        data = QueryDict(formdata)
        f = forms.AddCollectionForm(data)

        self.assertFalse(f.is_valid())
        self.assertTrue("path" in f.errors)
        errormsg = "This path doesn't exist"
        self.assertEqual(errormsg, f.errors["path"][0])

        # Now the first path exists but the second doesn't
        pathmock = mock.Mock(side_effect=[True, False])
        forms.os.path.exists = pathmock

        formdata = "collectionid=55412ad8-1b15-44d5-8dc8-9c3cb0cf9e5d&path=%2Fsome%2Fpath"
        data = QueryDict(formdata)
        f = forms.AddCollectionForm(data)

        self.assertFalse(f.is_valid())
        errormsg = "Path doesn't contain inner 'audio'"
        self.assertEqual(errormsg, f.errors["path"][0])

    def test_collection_bad_uuid(self):
        formdata = "collectionid=5xxxxxad8-1b15-44d5-8dc8-notauuid&path=%2Fsome%2Fpath"
        data = QueryDict(formdata)
        f = forms.AddCollectionForm(data)

        self.assertFalse(f.is_valid())
        self.assertTrue("collectionid" in f.errors)
        errormsg = "Collection ID needs to be a UUID"
        self.assertEqual(errormsg, f.errors["collectionid"][0])

    def test_collection_exists(self):
        models.Collection.objects.create(collectionid="55412ad8-1b15-44d5-8dc8-eeeeeeeeeeee", name="test collection")
        formdata = "collectionid=55412ad8-1b15-44d5-8dc8-eeeeeeeeeeee&path=%2Fsome%2Fpath"
        data = QueryDict(formdata)
        f = forms.AddCollectionForm(data)

        self.assertFalse(f.is_valid())
        self.assertTrue("collectionid" in f.errors)
        errormsg = "A collection with this ID already exists"
        self.assertEqual(errormsg, f.errors["collectionid"][0])

    def test_collection_musicbrainz_error(self):
        formdata = "collectionid=55412ad8-1b15-44d5-8dc8-eeeeeeeeeeee&path=%2Fpath%2Fpath"
        data = QueryDict(formdata)
        f = forms.AddCollectionForm(data)

        response = requests.Response()
        response.status_code = 404
        mockerror = mock.Mock(side_effect=forms.compmusic.musicbrainz.requests.HTTPError(response=response))
        forms.compmusic.musicbrainz.get_collection_name = mockerror

        self.assertFalse(f.is_valid())
        self.assertTrue("__all__" in f.errors)
        errormsg = "Cannot find this collection on MusicBrainz"
        self.assertEqual(errormsg, f.errors["__all__"][0])

        response = requests.Response()
        response.status_code = 503
        mockerror = mock.Mock(side_effect=forms.compmusic.musicbrainz.requests.HTTPError(response=response))
        forms.compmusic.musicbrainz.get_collection_name = mockerror
        f = forms.AddCollectionForm(data)
        self.assertFalse(f.is_valid())
        self.assertTrue("__all__" in f.errors)
        errormsg = "Error connecting to MusicBrainz, try again shortly"
        self.assertEqual(errormsg, f.errors["__all__"][0])

    def test_view(self):
        """test the actual creation of the collection objects"""
        self.client.force_login(self.user1)

        collid = "55412ad8-1b15-44d5-8dc8-9c3cb0cf9e5d"
        data = {"collectionid": collid, "path": "/incoming/carnatic"}

        mockimport = mock.Mock()
        views.jobs.force_load_and_import_collection = mockimport
        self.client.post("/dashboard/addcollection", data)

        # dashboard collection
        dashc = models.Collection.objects.get(collectionid=collid)
        self.assertEqual("/incoming/carnatic", dashc.root_directory)
        mockimport.assert_called_once_with(collid)

        # docserver collection
        docc = docserver.models.Collection.objects.get(collectionid=collid)
        self.assertEqual("/incoming/carnatic", docc.root_directory)
