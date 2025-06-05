from django.http import QueryDict
from django.test import TestCase

from docserver import forms, models


class SourceFileTypeTest(TestCase):
    def test_add_filetype(self):
        self.assertEqual(0, models.SourceFileType.objects.all().count())
        formdata = "slug=myslug&extension=ext&mimetype=application%2Ffoo&name=thename&stype=audio"
        data = QueryDict(formdata)
        f = forms.SourceFileTypeForm(data)
        self.assertEqual(f.errors, {})
        f.save()
        self.assertEqual(1, models.SourceFileType.objects.all().count())
        sf = models.SourceFileType.objects.get()
        self.assertEqual("application/foo", sf.mimetype)

    def test_add_existing_slug(self):
        models.SourceFileType.objects.create(slug="aslug", extension="x", mimetype="x", name="some filetype")
        formdata = "slug=aslug&extension=ext&mimetype=application%2Ffoo&name=thename&stype=data"
        data = QueryDict(formdata)
        f = forms.SourceFileTypeForm(data)
        self.assertFalse(f.is_valid())
        self.assertEqual(f.errors, {"slug": ["Slug already exists"]})
        self.assertEqual(1, len(f.errors))

    def test_rename_existing_slug(self):
        models.SourceFileType.objects.create(slug="aslug", extension="x", mimetype="x", name="some filetype")
        sf2 = models.SourceFileType.objects.create(slug="otherslug", extension="x", mimetype="x", name="some filetype")

        formdata = "slug=aslug&extension=ext&mimetype=application%2Ffoo&name=thename"
        data = QueryDict(formdata)
        f = forms.SourceFileTypeForm(data, instance=sf2)

        self.assertFalse(f.is_valid())
