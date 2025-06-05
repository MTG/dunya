import uuid

from django.test import TestCase

from makam import models


class FormTest(TestCase):
    def test_unaccent_get(self):
        f = models.Form.objects.create(name="Şarkı", uuid=uuid.uuid4())
        ret = models.Form.objects.get(name__unaccent__iexact="sarki")
        self.assertEqual(f, ret)

    def test_worklist(self):
        w = models.Work.objects.create(title="w")
        f = models.Form.objects.create(name="form", uuid=uuid.uuid4())
        w.form.add(f)
        self.assertTrue(w in f.worklist())
        self.assertEqual(1, len(f.worklist()))
