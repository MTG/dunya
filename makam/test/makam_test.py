import uuid

from django.test import TestCase

from makam import models


class MakamTest(TestCase):
    def setUp(self):
        self.w = models.Work.objects.create(title="w")
        self.r1 = models.Recording.objects.create(title="r1", has_taksim=True)
        self.r2 = models.Recording.objects.create(title="r2", has_gazel=True)
        self.m = models.Makam.objects.create(name="m", uuid=uuid.uuid4())
        self.w.makam.add(self.m)
        self.r1.makam.add(self.m)
        self.r2.makam.add(self.m)

    def test_unaccent_get(self):
        m = models.Makam.objects.create(name="Bûselik", uuid=uuid.uuid4())
        ret = models.Makam.objects.get(name__unaccent__iexact="buselik")
        self.assertEqual(m, ret)

        hm = models.Makam.objects.create(name="Hicaz Hümayun", uuid=uuid.uuid4())
        models.MakamAlias.objects.create(makam=hm, name="Hicaz-Hümayun")
        models.MakamAlias.objects.create(makam=hm, name="Hicaz-Hümâyûn")

        hma_all = models.MakamAlias.objects.filter(name__unaccent__iexact="hicaz-humayun").all()
        self.assertEqual(2, hma_all.count())

        try:
            hma_all = models.MakamAlias.objects.get(name__unaccent__iexact="hicaz-humayun")
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
