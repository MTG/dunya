from django.test import TestCase

from makam import models

class MakamTest(TestCase):
    def test_id_redirect(self):
        m = models.Makam.objects.create(name="Test makam")
        uuid = m.uuid
        id = m.pk

        resp = self.client.get("/makam/makam/%s" % id)
        self.assertRedirects(resp, "/makam/makam/%s/test-makam" % uuid, status_code=301)

class FormTest(TestCase):

    def test_id_redirect(self):
        f = models.Form.objects.create(name="Test form")
        uuid = f.uuid
        id = f.pk

        resp = self.client.get("/makam/form/%s" % id)
        self.assertRedirects(resp, "/makam/form/%s/test-form" % uuid, status_code=301)

class UsulTest(TestCase):
    def test_id_redirect(self):
        u = models.Usul.objects.create(name="Test usul")
        uuid = u.uuid
        id = u.pk

        resp = self.client.get("/makam/usul/%s" % id)
        self.assertRedirects(resp, "/makam/usul/%s/test-usul" % uuid, status_code=301)
