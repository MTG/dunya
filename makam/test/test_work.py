import uuid

from django.test import TestCase

from makam import models


class WorkTest(TestCase):
    # Work tests are simple because all methods just call foreign keys

    def test_recordinglist(self):
        r = models.Recording.objects.create(title="recording")
        w = models.Work.objects.create(title="work")
        models.RecordingWork.objects.create(recording=r, work=w, sequence=1)
        recs = w.recordinglist()
        self.assertEqual(1, len(recs))
        self.assertTrue(r in recs)

    def test_makamlist(self):
        w = models.Work.objects.create(title="work")
        m = models.Makam.objects.create(name="m", uuid=uuid.uuid4())
        w.makam.add(m)
        self.assertTrue(m in w.makamlist())

    def test_usullist(self):
        w = models.Work.objects.create(title="work")
        u = models.Usul.objects.create(name="u", uuid=uuid.uuid4())
        w.usul.add(u)
        self.assertTrue(u in w.usullist())

    def test_formlist(self):
        w = models.Work.objects.create(title="work")
        f = models.Form.objects.create(name="f", uuid=uuid.uuid4())
        w.form.add(f)
        self.assertTrue(f in w.formlist())

    def test_composerlist(self):
        w = models.Work.objects.create(title="work")
        c = models.Composer.objects.create(name="composer")
        w.composers.add(c)
        self.assertTrue(c in w.composerlist())

    def test_lyricistlist(self):
        w = models.Work.objects.create(title="work")
        c = models.Composer.objects.create(name="composer")
        w.lyricists.add(c)
        self.assertTrue(c in w.lyricistlist())
