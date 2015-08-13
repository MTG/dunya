from django.test import TestCase

from kvedit import models

class CategoryTest(TestCase):
    def setUp(self):
        self.c = models.Category.objects.create(name='cat')

        self.i1 = models.Item.objects.create(category=self.c, ref='item1')
        self.i2 = models.Item.objects.create(category=self.c, ref='item2')

        models.Field.objects.create(item=self.i1, key="k1", value="v1")
        models.Field.objects.create(item=self.i1, key="k2", value="v2")
        models.Field.objects.create(item=self.i2, key="k3", value="v3")
        models.Field.objects.create(item=self.i2, key="k4", value="v4")

    def test_category_to_object(self):
        ret = self.c.to_object()
        expected = [{"k1": "v1", "k2": "v2"},{"k3": "v3", "k4": "v4"}]

        self.assertItemsEqual(expected, ret)

    def test_item_to_object(self):
        ret = self.i1.to_object()
        expected = {"k1": "v1", "k2": "v2"}
        self.assertEqual(expected, ret)
