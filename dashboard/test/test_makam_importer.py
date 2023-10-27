import uuid

from django.test import TestCase

from dashboard import makam_importer
from makam import models


class MakamImporterTest(TestCase):
    def setUp(self):
        self.mi = makam_importer.MakamReleaseImporter(None)

    def test_get_makam(self):
        # Makam that exists
        m = models.Makam.objects.create(name="A makam", uuid=str(uuid.uuid4()))
        get_m = self.mi._get_makam("a makam")
        self.assertEqual(m, get_m)

        # Makam alias that exists
        ma = models.MakamAlias.objects.create(makam=m, name="alias makam")
        get_m = self.mi._get_makam("alias makam")
        self.assertEqual(m, get_m)

        # 2 aliases with the same unaccent() representation
        hm = models.Makam.objects.create(name="Hicaz Hümayun", uuid=str(uuid.uuid4()))
        hma1 = models.MakamAlias.objects.create(makam=hm, name="Hicaz-Hümayun")
        hma2 = models.MakamAlias.objects.create(makam=hm, name="Hicaz-Hümâyûn")

        get_m = self.mi._get_makam("hicaz-humayun")
        self.assertEqual(hm, get_m)

        # Something that doesn't exist
        get_m = self.mi._get_makam("Not a makam")
        self.assertEqual(None, get_m)

