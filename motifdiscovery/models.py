from django.db import models
from django_extensions.db.fields import UUIDField

class MotifManager(models.Manager):
    def get_queryset(self):
        return super(MotifManager, self).get_queryset().using('motif')

class File(models.Model):
    objects = MotifManager()

    filename = models.CharField(max_length=1000)
    mbid = UUIDField(blank=True, null=True)
    hasseed = models.IntegerField()

    def __unicode__(self):
        return u"%s (%s) [%s]" % (self.filename, self.mbid, self.hasseed)

class Match(models.Model):
    objects = MotifManager()

    source = models.ForeignKey("Pattern", related_name='match_sources')
    target = models.ForeignKey("Pattern", related_name='match_targets')
    distance = models.FloatField()
    version = models.IntegerField()

    def __unicode__(self):
        return u"%s, %s (%s) [%s]" % (self.source, self.target, self.distance, self.version)

class Pattern(models.Model):
    objects = MotifManager()

    file = models.ForeignKey(File)
    start_time = models.FloatField()
    end_time = models.FloatField()
    pair_id = models.IntegerField(blank=True, null=True)
    isseed = models.IntegerField()
    segment = models.ForeignKey("Segment", related_name='patterns', blank=True, null=True)

    def __unicode__(self):
        return u"File %s (%s - %s) [%s, %s]" % (self.file.mbid, self.start_time, self.end_time, self.isseed, self.pair_id)

class Segment(models.Model):
    objects = MotifManager()

    file = models.ForeignKey(File)
    rounded_start = models.FloatField()
    rounded_end = models.FloatField()
    segment_path = models.CharField(max_length=500)

    def __unicode__(self):
        return u"segment of %s (%s-%s)" % (self.file, self.rounded_start, self.rounded_end)
