from django.test import TestCase

from hindustani import models

class InstrumentTest(TestCase):
    fixtures = ['hindustani_instrument']
    def test_hidden_instrument(self):

        # Not hidden
        resp = self.client.get("/hindustani/instrument/4")
        self.assertEqual(resp.status_code, 200)

        # hidden
        resp = self.client.get("/hindustani/instrument/5")
        self.assertEqual(resp.status_code, 404)
