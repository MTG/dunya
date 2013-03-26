from django.db import models
from django_extensions.db.fields import UUIDField
from django.core.urlresolvers import reverse

class SourceName(models.Model):
    name = models.CharField(max_length=100)

class Source(models.Model):
    source_name = models.ForeignKey(SourceName)
    uri = models.CharField(max_length=255)

class BaseModel(models.Model):
    class Meta:
        abstract = True

    source = models.ForeignKey(Source, blank=True, null=True)

    def get_style(self):
        raise Exception("need style")

    def get_object_map(self, key):
        """ Returns a dict with keys 'artist', recording,
            release, work, performance mapping to 
            local classes that are the correct type"""
        raise Exception("need map")

class Artist(BaseModel):
    class Meta:
        abstract = True

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female')
    )
    TYPE_CHOICES = (
        ('P', 'Person'),
        ('G', 'Group')
    )
    name = models.CharField(max_length=200)
    mbid = UUIDField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    startdate = models.DateField(blank=True, null=True)
    enddate = models.DateField(blank=True, null=True)
    artist_type = models.CharField(max_length=1, choices=TYPE_CHOICES, default='P')
    main_instrument = models.ForeignKey('Instrument', blank=True, null=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        viewname = "%s-artist" % (self.get_style(), )
        return reverse(viewname, args=[str(self.id)])

    def performances(self):
        ConcertClass = self.get_object_map("concert")
        IPClass = self.get_object_map("performance")
        concerts = ConcertClass.objects.filter(tracks__instrumentperformance__performer=self).distinct()
        ret = []
        for c in concerts:
            performances = InstrumentPerformance.objects.filter(performer=self, recording__concerts=c).distinct()
            ret.append((c, performances))
        return ret

class Concert(BaseModel):
    class Meta:
        abstract = True
    mbid = UUIDField(blank=True, null=True)
    location = models.ForeignKey('Location', blank=True, null=True)
    title = models.CharField(max_length=100)
    artists = models.ManyToManyField('Artist')
    tracks = models.ManyToManyField('Recording')

    def __unicode__(self):
        ret = ", ".join([unicode(a) for a in self.artists.all()])
        if self.location:
            ret += " at " + unicode(self.location)
        return "%s (%s)" % (self.title, ret)

    def get_absolute_url(self):
        viewname = "%s-concert" % (self.get_style(), )
        return reverse(viewname, args=[str(self.id)])

    def performers(self):
        ArtistClass = self.get_object_map()["artist"]
        return ArtistClass.objects.filter(instrumentperformance__recording__in=self.tracks.all()).distinct().all()

class Work(BaseModel):
    class Meta:
        abstract = True
    title = models.CharField(max_length=100)
    mbid = UUIDField(blank=True, null=True)
    composer = models.ForeignKey('Composer', blank=True, null=True)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        viewname = "%s-work" % (self.get_style(), )
        return reverse(viewname, args=[str(self.id)])

    def concerts(self):
        return Concert.objects.filter(tracks__work=self).all()

class WorkAttribute(models.Model):
    class Meta:
        abstract = True
    work = models.ForeignKey('Work')
    attribute_type = models.ForeignKey('WorkAttributeType')
    attribute_value_free = models.CharField(max_length=100, blank=True, null=True)
    attribute_value = models.ForeignKey('WorkAttributeTypeValue', blank=True, null=True)

class WorkAttributeType(models.Model):
    class Meta:
        abstract = True
    type_name = models.CharField(max_length=100)

class WorkAttributeTypeValue(models.Model):
    class Meta:
        abstract = True
    attribute_type = models.ForeignKey('WorkAttributeType')
    value = models.CharField(max_length=100)

class Recording(BaseModel):
    class Meta:
        abstract = True
    title = models.CharField(max_length=100)
    work = models.ForeignKey('Work', blank=True, null=True)
    mbid = UUIDField(blank=True, null=True)
    length = models.IntegerField(blank=True, null=True)
    performance = models.ManyToManyField('Artist', through="InstrumentPerformance")

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        viewname = "%s-recording" % (self.get_style(), )
        return reverse(viewname, args=[str(self.id)])

    def all_artists(self):
        return Artist.objects.filter(concert__tracks=self)

class Instrument(BaseModel):
    class Meta:
        abstract = True
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        viewname = "%s-instrument" % (self.get_style(), )
        return reverse(viewname, args=[str(self.id)])

    def artists(self):
        return Artist.objects.filter(instrumentperformance__instrument=self).distinct().all()

class InstrumentPerformance(models.Model):
    class Meta:
        abstract = True
    recording = models.ForeignKey('Recording')
    performer = models.ForeignKey('Artist')
    instrument = models.ForeignKey('Instrument')
    lead = models.BooleanField(default=False)


class Composer(BaseModel):
    class Meta:
        abstract = True
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female')
    )
    name = models.CharField(max_length=200)
    mbid = UUIDField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    startdate = models.DateField(blank=True, null=True)
    enddate = models.DateField(blank=True, null=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        viewname = "%s-composer" % (self.get_style(), )
        return reverse(viewname, args=[str(self.id)])

    def raagas(self):
        return Raaga.objects.filter(work__composer=self).all()

    def taalas(self):
        return Taala.objects.filter(work__composer=self).all()

class Location(BaseModel):
    class Meta:
        abstract = True
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    lat = models.CharField(max_length=10, blank=True, null=True)
    lng = models.CharField(max_length=10, blank=True, null=True)

    def __unicode__(self):
        return self.name

