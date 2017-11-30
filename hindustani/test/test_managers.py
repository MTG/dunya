# coding=utf-8

from django.test import TestCase

from hindustani import models


class RaagTestCase(TestCase):
    fixtures = ['hindustani_raag']

    def test_fuzzy(self):
        # name
        r = models.Raag.objects.fuzzy('Adānā malhār')
        self.assertEqual(4, r.id)

        # common name
        r = models.Raag.objects.fuzzy('Adana malhar')
        self.assertEqual(4, r.id)

        # alias
        r = models.Raag.objects.fuzzy('Bilaskhani')
        self.assertEqual(41, r.id)


class TaalTestCase(TestCase):
    fixtures = ['hindustani_taal']

    def test_fuzzy(self):
        # name
        t = models.Taal.objects.fuzzy('Ādhā cautāl')
        self.assertEqual(2, t.id)

        # common name
        t = models.Taal.objects.fuzzy('Ada chautal')
        self.assertEqual(2, t.id)

        # alias
        t = models.Taal.objects.fuzzy('adachautal')
        self.assertEqual(2, t.id)


class FormTestCase(TestCase):

    fixtures = ['hindustani_form']

    def test_fuzzy(self):
        # name
        t = models.Form.objects.fuzzy('Kajarī')
        self.assertEqual(21, t.id)

        # common name
        t = models.Form.objects.fuzzy('Kajari')
        self.assertEqual(21, t.id)

        # alias
        t = models.Form.objects.fuzzy('kajri')
        self.assertEqual(21, t.id)


class LayaTestCase(TestCase):

    fixtures = ['hindustani_laya']

    def test_fuzzy(self):
        # name
        t = models.Laya.objects.fuzzy('Dr̥t')
        self.assertEqual(4, t.id)

        # common name
        t = models.Laya.objects.fuzzy('drut')
        self.assertEqual(4, t.id)

        # alias
        t = models.Laya.objects.fuzzy('dhrut')
        self.assertEqual(4, t.id)
