from django.test import TestCase

from hindustani import models
import uuid

class InstrumentTest(TestCase):
    fixtures = ['hindustani_instrument']
    def test_hidden_instrument(self):

        # Not hidden
        resp = self.client.get("/hindustani/instrument/1ebfe130-b68c-452a-8ee3-81b430d13ca3")
        self.assertEqual(resp.status_code, 200)

        # hidden
        resp = self.client.get("/hindustani/instrument/0fe1a768-45ba-49e4-8363-14db8e73ca85")
        self.assertEqual(resp.status_code, 404)

class RaagTest(TestCase):
    fixtures = ['hindustani_laya']

    def test_id_redirect(self):
        r = models.Raag.objects.create(name="Test raag", common_name="Test raag", uuid=str(uuid.uuid4()))
        uid = r.uuid
        id = r.pk

        resp = self.client.get("/hindustani/raag/%s" % id)
        self.assertRedirects(resp, "/hindustani/raag/%s/test-raag" % uid, status_code=301)

class TaalTest(TestCase):
    fixtures = ['hindustani_laya']

    def test_id_redirect(self):
        t = models.Taal.objects.create(name="Test taal", common_name="Test taal", uuid=str(uuid.uuid4()))
        uid = t.uuid
        id = t.pk

        resp = self.client.get("/hindustani/taal/%s" % id)
        self.assertRedirects(resp, "/hindustani/taal/%s/test-taal" % uid, status_code=301)

class LayaTest(TestCase):
    fixtures = ['hindustani_laya']

    def test_id_redirect(self):
        l = models.Laya.objects.create(name="Test laya", common_name="Test laya", uuid=str(uuid.uuid4()))
        uid = l.uuid
        id = l.pk

        resp = self.client.get("/hindustani/laya/%s" % id)
        self.assertRedirects(resp, "/hindustani/laya/%s/test-laya" % uid, status_code=301)

class FormTest(TestCase):
    fixtures = ['hindustani_laya']

    def test_id_redirect(self):
        f = models.Form.objects.create(name="Test form", common_name="Test form", uuid=str(uuid.uuid4()))
        uid = f.uuid
        id = f.pk

        resp = self.client.get("/hindustani/form/%s" % id)
        self.assertRedirects(resp, "/hindustani/form/%s/test-form" % uid, status_code=301)
