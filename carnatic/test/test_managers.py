# coding=utf-8
from django.test import TestCase

from carnatic import models


class RaagaManagerTest(TestCase):

    fixtures = ['carnatic_raaga']

    def test_fuzzy(self):
        # name
        r = models.Raaga.objects.fuzzy('Ārabhi')
        self.assertEqual(4, r.id)

        # common name
        r = models.Raaga.objects.fuzzy('arabhi')
        self.assertEqual(4, r.id)

        # alias
        r = models.Raaga.objects.fuzzy('aarabhi')
        self.assertEqual(4, r.id)


class TaalaManagerTest(TestCase):

    fixtures = ['carnatic_taala']

    def test_fuzzy(self):
        # name
        t = models.Taala.objects.fuzzy('Ādi')
        self.assertEqual(1, t.id)

        # common name
        t = models.Taala.objects.fuzzy('adi')
        self.assertEqual(1, t.id)

        # alias
        t = models.Taala.objects.fuzzy('aadi')
        self.assertEqual(1, t.id)


class FormManagerTest(TestCase):

    fixtures = ['carnatic_form']

    def test_fuzzy(self):
        # name
        f = models.Form.objects.fuzzy('Alapana')
        self.assertEqual(1, f.id)


class InstrumentManagerTest(TestCase):

    fixtures = ['carnatic_instrument']

    def test_fuzzy(self):
        # name
        i = models.Instrument.objects.fuzzy('Khanjira')
        self.assertEqual(10, i.id)

        # alias
        i = models.Instrument.objects.fuzzy('kanjira')
        self.assertEqual(10, i.id)
