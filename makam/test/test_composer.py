from django.test import TestCase

from makam import models


class ComposerTest(TestCase):
    def setUp(self):
        self.c1 = models.Composer.objects.create(name="c1")
        self.c2 = models.Composer.objects.create(name="c2")
        self.w1 = models.Work.objects.create(title="w1")
        self.w1.lyricists.add(self.c1)
        self.w1.composers.add(self.c2)

    def test_works(self):
        self.assertTrue(self.w1 in self.c1.lyricworklist())
        self.assertEqual(0, len(self.c1.worklist()))

    def test_lyrics_works(self):
        self.assertTrue(self.w1 in self.c2.worklist())
        self.assertEqual(0, len(self.c2.lyricworklist()))
