# -*- coding: UTF-8 -*-

from django.test import TestCase

from makam import models

class MakamTest(TestCase):
    def setUp(self):
        self.w = models.Work.objects.create(title="w")
        self.r1 = models.Recording.objects.create(title="r1", has_taksim=True)
        self.r2 = models.Recording.objects.create(title="r2", has_gazel=True)
        self.m = models.Makam.objects.create(name="m")
        self.w.makam.add(self.m)
        self.r1.makam.add(self.m)
        self.r2.makam.add(self.m)

    def test_unaccent_get(self):
        m = models.Makam.objects.create(name=u"Bûselik")
        ret = models.Makam.objects.unaccent_get("buselik")
        self.assertEqual(m, ret)

        hm = models.Makam.objects.create(name=u"Hicaz Hümayun")
        hma1 = models.MakamAlias.objects.create(makam=hm, name=u"Hicaz-Hümayun")
        hma2 = models.MakamAlias.objects.create(makam=hm, name=u"Hicaz-Hümâyûn")

        hma_all = models.MakamAlias.objects.unaccent_all("hicaz-humayun")
        self.assertEqual(2, hma_all.count())

        try:
            hma_all = models.MakamAlias.objects.unaccent_get("hicaz-humayun")
            # Shouldn't get here
            self.assertTrue(False)
        except models.MakamAlias.MultipleObjectsReturned:
            pass

    def test_worklist(self):
        self.assertTrue(self.w in self.m.worklist())
        self.assertEqual(1, len(self.m.worklist()))

    def test_taksimlist(self):
        self.assertEqual(1, len(self.m.taksimlist()))
        self.assertTrue(self.r1 in self.m.taksimlist())

    def test_gazellist(self):
        self.assertEqual(1, len(self.m.gazellist()))
        self.assertTrue(self.r2 in self.m.gazellist())

