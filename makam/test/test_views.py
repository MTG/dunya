import mock
from django.http import HttpResponseNotFound, Http404, HttpResponse
from django.test import TestCase

import docserver.models
import docserver.views
from makam import models


class SymbTrTest(TestCase):
    def setUp(self):
        self.test_uuid = "721ae3da-ed63-4ad7-86d9-ac2c9a4ab039"
        self.symbtr = models.SymbTr.objects.create(uuid=self.test_uuid, name="test_symbtr")

    @mock.patch('docserver.views.download_external')
    def test_successful(self, download):
        download.return_value = HttpResponse('ok')
        sft = docserver.models.SourceFileType.objects.create(slug="symbtrtxt", extension="txt", mimetype="")

        resp = self.client.get("/makam/symbtr/%s" % self.test_uuid)
        download.assert_called_with(mock.ANY, self.test_uuid, "symbtrtxt")
        self.assertEqual(resp.status_code, 200)

    def test_format_invalid(self):
        # a type that is not valid
        resp = self.client.get("/makam/symbtr/%s?format=nono" % self.test_uuid)
        self.assertEqual(resp.status_code, 400)

    @mock.patch('makam.views.get_object_or_404')
    def test_format_missing(self, obj404):
        # a type that is valid but doesn't exist for some reason
        obj404.side_effect = [self.symbtr, Http404()]
        docserver.views.download_external = mock.Mock(return_value=HttpResponse('ok'))
        resp = self.client.get("/makam/symbtr/%s?format=pdf" % self.test_uuid)

        self.assertEqual(resp.status_code, 404)
        calls = [mock.call(models.SymbTr, uuid=self.test_uuid),
                 mock.call(docserver.models.SourceFileType, slug="symbtrpdf")]
        obj404.assert_has_calls(calls)

    @mock.patch('makam.views.get_object_or_404')
    def test_no_symbtr(self, obj404):
        obj404.side_effect = Http404()
        other_uuid = "721ae3da-ed63-4ad7-86d9-ac2c9a4aaaaa"
        resp = self.client.get("/makam/symbtr/%s" % other_uuid)
        self.assertEqual(resp.status_code, 404)
        calls = [mock.call(models.SymbTr, uuid=other_uuid)]
        obj404.assert_has_calls(calls)

    @mock.patch('docserver.views.download_external')
    def test_no_doc(self, download):
        download.return_value = HttpResponseNotFound('x')
        sft = docserver.models.SourceFileType.objects.create(slug="symbtrtxt", extension="txt", mimetype="")
        resp = self.client.get("/makam/symbtr/%s?format=txt" % self.test_uuid)

        self.assertEqual(resp.status_code, 404)
        download.assert_called_with(mock.ANY, self.test_uuid, "symbtrtxt")
