# -*- coding: UTF-8 -*-

from django.test import TestCase

from makam import models


class UsulTest(TestCase):
    def setUp(self):
        self.w = models.Work.objects.create(title="w")
        self.u = models.Usul.objects.create(name="u")
        self.w.usul.add(self.u)

    def test_unaccent_get(self):
        u = models.Usul.objects.create(name=u"Çeng-i Harbî")
        ret = models.Usul.objects.unaccent_get("ceng-i harbi")
        self.assertEqual(u, ret)

    def test_worklist(self):
        self.assertTrue(self.w in self.u.worklist())
        self.assertEqual(1, len(self.u.worklist()))
