from django.test import TestCase

from makam import models


class UsulTest(TestCase):
    def setUp(self):
        self.w = models.Work.objects.create(title="w")
        self.u = models.Usul.objects.create(name="u", uuid="d5e15ee7-e6c3-4148-845c-8e7610c619e9")
        self.w.usul.add(self.u)

    def test_unaccent_get(self):
        u = models.Usul.objects.create(name="Çeng-i Harbî", uuid="d5e15ee7-e6c3-4148-845c-8e7610c619e9")
        ret = models.Usul.objects.get(name__unaccent__iexact="ceng-i harbi")
        self.assertEqual(u, ret)

    def test_worklist(self):
        self.assertTrue(self.w in self.u.worklist())
        self.assertEqual(1, len(self.u.worklist()))
