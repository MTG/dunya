from django.test import TestCase

from makam import models

class RecordingTest(TestCase):
    fixtures = ["makam_instrument"]

    def test_releaselist(self):
        rel1 = models.Release.objects.create(title="rel1")
        rel2 = models.Release.objects.create(title="rel2")
        rel3 = models.Release.objects.create(title="rel3")

        rec1 = models.Recording.objects.create(title="rec1")
        rec2 = models.Recording.objects.create(title="rec2")
        rec3 = models.Recording.objects.create(title="rec3")

        # Recording 1 is part of releases 1 and 2
        models.ReleaseRecording.objects.create(release=rel1, recording=rec1, track=1)
        models.ReleaseRecording.objects.create(release=rel2, recording=rec1, track=1)
        # Recording 2 is only release 1
        models.ReleaseRecording.objects.create(release=rel1, recording=rec2, track=2)
        # Recording 3, release 3
        models.ReleaseRecording.objects.create(release=rel3, recording=rec3, track=1)

        rels = rec1.releaselist()
        self.assertEqual(2, len(rels))
        self.assertTrue(rel1 in rels)
        self.assertTrue(rel2 in rels)

        rels = rec2.releaselist()
        self.assertEqual(1, len(rels))
        self.assertTrue(rel1 in rels)

        rels = rec3.releaselist()
        self.assertEqual(1, len(rels))
        self.assertTrue(rel3 in rels)

    def test_worklist(self):
        # If works are added to the db out of order they are listed correctly
        rec = models.Recording.objects.create(title="recording")
        wk1 = models.Work.objects.create(title="work1")
        wk2 = models.Work.objects.create(title="work2")
        models.RecordingWork.objects.create(recording=rec, work=wk2, sequence=2)
        models.RecordingWork.objects.create(recording=rec, work=wk1, sequence=1)

        works = rec.worklist()
        self.assertEqual(2, len(works))
        self.assertEqual(wk1, works[0])
        self.assertEqual(wk2, works[1])

    def test_performers(self):
        # If a recording is part of 2 releases and each release has the same main
        # artist, don't duplicate this artist
        rel1 = models.Release.objects.create(title="rel1")
        rel2 = models.Release.objects.create(title="rel2")

        rec1 = models.Recording.objects.create(title="rec1")
        a = models.Artist.objects.create(name="a1")
        rel1.artists.add(a)
        rel2.artists.add(a)
        models.ReleaseRecording.objects.create(release=rel1, recording=rec1, track=1)
        models.ReleaseRecording.objects.create(release=rel2, recording=rec1, track=1)

        artists = rec1.performers()
        self.assertEqual(1, len(artists))
        self.assertEqual([a], artists)

        # If an artist is on the release and a perf relationship, don't duplicate
        rel3 = models.Release.objects.create(title="rel3")
        rec2 = models.Recording.objects.create(title="rec2")
        a2 = models.Artist.objects.create(name="a2")
        rel3.artists.add(a, a2)
        models.ReleaseRecording.objects.create(release=rel3, recording=rec2, track=1)
        models.InstrumentPerformance.objects.create(recording=rec2, artist=a2)

        artists = rec2.performers()
        self.assertEqual(2, len(artists))
        self.assertTrue(a in artists)
        self.assertTrue(a2 in artists)

        # If another artist plays on a different recording, don't show it
        a3 = models.Artist.objects.create(name="a3")
        rec3 = models.Recording.objects.create(title="rec3")
        models.ReleaseRecording.objects.create(release=rel3, recording=rec3, track=2)
        models.InstrumentPerformance.objects.create(recording=rec3, artist=a3)

        artists = rec2.performers()
        self.assertEqual(2, len(artists))
        self.assertTrue(a3 not in artists)

    def test_instruments_for_artist(self):
        # If this artist is only on the release artist, no instrument
        a1 = models.Artist.objects.create(name="a1")
        rel = models.Release.objects.create(title="release")
        rel.artists.add(a1)
        rec1 = models.Recording.objects.create(title="rec1")
        models.ReleaseRecording.objects.create(release=rel, recording=rec1, track=1)

        insts = rec1.instruments_for_artist(a1)
        self.assertEqual(0, len(insts))

        # Plays more than 1
        i1 = models.Instrument.objects.all()[1]
        i2 = models.Instrument.objects.all()[2]
        models.InstrumentPerformance.objects.create(recording=rec1, artist=a1, instrument=i1)
        models.InstrumentPerformance.objects.create(recording=rec1, artist=a1, instrument=i2)
        insts = rec1.instruments_for_artist(a1)
        self.assertEqual(2, len(insts))
        self.assertTrue(i1 in insts)
        self.assertTrue(i2 in insts)

        # Artist plays a different instrument on a different recording
        i3 = models.Instrument.objects.all()[3]
        rec2 = models.Recording.objects.create(title="rec2")
        models.ReleaseRecording.objects.create(release=rel, recording=rec2, track=2)
        models.InstrumentPerformance.objects.create(recording=rec2, artist=a1, instrument=i3)
        insts = rec1.instruments_for_artist(a1)
        self.assertTrue(i3 not in insts)
        insts = rec2.instruments_for_artist(a1)
        self.assertEqual(1, len(insts))
        self.assertTrue(i3 in insts)
