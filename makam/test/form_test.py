# -*- coding: UTF-8 -*-

from django.test import TestCase

from makam import models


class FormTest(TestCase):

    def test_unaccent_get(self):
        f = models.Form.objects.create(name=u"Şarkı")
        ret = models.Form.objects.unaccent_get("sarki")
        self.assertEqual(f, ret)

    def test_worklist(self):
        w = models.Work.objects.create(title="w")
        f = models.Form.objects.create(name="form")
        w.form.add(f)
        self.assertTrue(w in f.worklist())
        self.assertEqual(1, len(f.worklist()))
