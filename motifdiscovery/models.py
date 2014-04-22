from django.db import models
from django_extensions.db.fields import UUIDField

class File(models.Model):
    filename = models.CharField(max_length=1000)
    mbid = UUIDField(blank=True, null=True)
    hasseed = models.IntegerField()

    def __unicode__(self):
        return u"%s (%s) [%s]" % (self.filename, self.mbid, self.hasseed)

class Match(models.Model):
    source = models.ForeignKey("Pattern", related_name='match_sources')
    target = models.ForeignKey("Pattern", related_name='match_targets')
    distance = models.FloatField()
    version = models.IntegerField()

    def __unicode__(self):
        return u"%s, %s (%s) [%s]" % (self.source, self.target, self.distance, self.version)

class Pattern(models.Model):
    file = models.ForeignKey(File)
    start_time = models.FloatField()
    end_time = models.FloatField()
    pair_id = models.IntegerField(blank=True, null=True) # ForeignKey to Pattern
    isseed = models.IntegerField()

    def __unicode__(self):
        return u"File %s (%s - %s) [%s, %s]" % (self.file.mbid, self.start_time, self.end_time, self.isseed, self.pair_id)

