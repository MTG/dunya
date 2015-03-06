from django.test import TestCase
from django.http import QueryDict

from mock import Mock
import StringIO

from dashboard import forms
from dashboard import models


class CollectionTest(TestCase):
    def setUp(self):
        models.CompletenessChecker.objects.create(pk=1, name="Completeness-1")
        models.CompletenessChecker.objects.create(pk=2, name="Completeness-1")

        self.mockname = Mock(return_value="My collection")
        forms.compmusic.musicbrainz.get_collection_name = self.mockname
        self.pathmock = Mock(return_value=True)
        forms.os.path.exists = self.pathmock

    def test_add_collection(self):
        formdata = "collectionid=55412ad8-1b15-44d5-8dc8-9c3cb0cf9e5d&path=%2Fsome%2Fpath&checkers=1&checkers=2"
        data = QueryDict(formdata)
        f = forms.AddCollectionForm(data)

        self.assertTrue(f.is_valid())
        self.assertEquals("My collection", f.cleaned_data["collectionname"])
        self.mockname.assert_called_once_with("55412ad8-1b15-44d5-8dc8-9c3cb0cf9e5d")
        self.pathmock.assert_called_once_with("/some/path")

    def test_no_path(self):
        pathmock = Mock(return_value=False)
        forms.os.path.exists = pathmock

        formdata = "collectionid=55412ad8-1b15-44d5-8dc8-9c3cb0cf9e5d&path=%2Fsome%2Fpath&checkers=1&checkers=2"
        data = QueryDict(formdata)
        f = forms.AddCollectionForm(data)

        self.assertFalse(f.is_valid())
        self.assertTrue("path" in f.errors)
        errormsg = "This path doesn't exist"
        self.assertEqual(errormsg, f.errors["path"][0])

    def test_collection_bad_uuid(self):
        formdata = "collectionid=5xxxxxad8-1b15-44d5-8dc8-notauuid&path=%2Fsome%2Fpath&checkers=1&checkers=2"
        data = QueryDict(formdata)
        f = forms.AddCollectionForm(data)

        self.assertFalse(f.is_valid())
        self.assertTrue("collectionid" in f.errors)
        errormsg = "Collection ID needs to be a UUID"
        self.assertEqual(errormsg, f.errors["collectionid"][0])


    def test_collection_exists(self):
        models.Collection.objects.create(pk="55412ad8-1b15-44d5-8dc8-eeeeeeeeeeee", name="test collection")
        formdata = "collectionid=55412ad8-1b15-44d5-8dc8-eeeeeeeeeeee&path=%2Fsome%2Fpath&checkers=1&checkers=2"
        data = QueryDict(formdata)
        f = forms.AddCollectionForm(data)

        self.assertFalse(f.is_valid())
        self.assertTrue("collectionid" in f.errors)
        errormsg = "A collection with this ID already exists"
        self.assertEqual(errormsg, f.errors["collectionid"][0])

    def test_collection_musicbrainz_error(self):
        formdata = "collectionid=55412ad8-1b15-44d5-8dc8-eeeeeeeeeeee&path=%2Fpath%2Fpath&checkers=1&checkers=2"
        data = QueryDict(formdata)
        f = forms.AddCollectionForm(data)

        url = "http://example.com"
        code = 404
        msg = "Not found"
        hdrs = {}
        fp = StringIO.StringIO()
        mockerror = Mock(side_effect=forms.compmusic.musicbrainz.urllib2.HTTPError(url, code, msg, hdrs, fp))
        forms.compmusic.musicbrainz.get_collection_name = mockerror

        self.assertFalse(f.is_valid())
        self.assertTrue("__all__" in f.errors)
        errormsg = "Cannot find this collection on MusicBrainz"
        self.assertEqual(errormsg, f.errors["__all__"][0])

        code = 503
        mockerror = Mock(side_effect=forms.compmusic.musicbrainz.urllib2.HTTPError(url, code, msg, hdrs, fp))
        forms.compmusic.musicbrainz.get_collection_name = mockerror
        f = forms.AddCollectionForm(data)
        self.assertFalse(f.is_valid())
        self.assertTrue("__all__" in f.errors)
        errormsg = "Error connecting to MusicBrainz, try again shortly"
        self.assertEqual(errormsg, f.errors["__all__"][0])

