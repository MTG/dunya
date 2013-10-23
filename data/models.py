from django.db import models
from django_extensions.db.fields import UUIDField
from django.core.urlresolvers import reverse
from django.conf import settings
import os

class SourceName(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

class Source(models.Model):
    # The source type that we got this data from (wikipedia, musicbrainz, etc)
    source_name = models.ForeignKey(SourceName)
    # The title of the page on the source website
    title = models.CharField(max_length=255)
    # The URL of the source
    uri = models.CharField(max_length=255)
    last_updated = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "From %s: %s (%s)" % (self.source_name, self.uri, self.last_updated)

class Description(models.Model):
    """ A short description of a thing in the database.
    It could be a biography, or a description """
    source = models.ForeignKey(Source, blank=True, null=True)
    description = models.TextField()

    def __unicode__(self):
        return "%s - %s" % (self.source, self.description[:100])

class Image(models.Model):
    """ An image of a thing in the database """
    source = models.ForeignKey(Source, blank=True, null=True)
    image = models.ImageField(upload_to="images")

    def __unicode__(self):
        ret = "%s" % (self.image.name, )
        if self.source:
            ret = "%s from %s" % (ret, self.source.uri)
        return ret

class BaseModel(models.Model):
    class Meta:
        abstract = True

    source = models.ForeignKey(Source, blank=True, null=True, related_name="%(class)s_source_set")
    references = models.ManyToManyField(Source, blank=True, null=True, related_name="%(class)s_reference_set")
    description = models.ForeignKey(Description, blank=True, null=True)
    images = models.ManyToManyField(Image, related_name="%(class)s_image_set")

    def ref(self):
        u = {"url": self.source.uri, "title": self.source.source_name.name}
        return u
        return [u]

    def get_style(self):
        raise Exception("need style")

    def get_object_map(self, key):
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
    begin = models.CharField(max_length=10, blank=True, null=True)
    end = models.CharField(max_length=10, blank=True, null=True)
    artist_type = models.CharField(max_length=1, choices=TYPE_CHOICES, default='P')
    main_instrument = models.ForeignKey('Instrument', blank=True, null=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        viewname = "%s-artist" % (self.get_style(), )
        return reverse(viewname, args=[str(self.id)])

    def get_image_url(self):
        media = settings.MEDIA_URL
        if self.images.all():
            image = self.images.all()[0]
            return os.path.join(media, image.image.name)
        else:
            return os.path.join(media, "missing", "artist.jpg")

    def get_musicbrainz_url(self):
        return "http://musicbrainz.org/artist/%s" % self.mbid

    def recordings(self):
        perfs = self.performances()
        IPClass = self.get_object_map("performance")
        performances = IPClass.objects.filter(performer=self)
        recs = [p.recording for p in performances]
        return recs

    def main_instrument(self):
        InstrClass = self.get_object_map("instrument")
        return InstrClass.objects.all()[0]

    def performances(self):
        ConcertClass = self.get_object_map("concert")
        IPClass = self.get_object_map("performance")
        concerts = ConcertClass.objects.filter(tracks__instrumentperformance__performer=self).distinct()
        ret = []
        for c in concerts:
            performances = IPClass.objects.filter(performer=self, recording__concert=c).distinct()
            # Unique the instrument list
            instruments = []
            theperf = []
            for p in performances:
                if p.instrument not in instruments:
                    theperf.append(p)
                    instruments.append(p.instrument)
            ret.append((c, theperf))
        return ret

class Label(BaseModel):
    name = models.CharField(max_length=100)

class Concert(BaseModel):
    class Meta:
        abstract = True
    mbid = UUIDField(blank=True, null=True)
    location = models.ForeignKey('Location', blank=True, null=True)
    title = models.CharField(max_length=100)
    artists = models.ManyToManyField('Artist')
    artistcredit = models.CharField(max_length=255)
    tracks = models.ManyToManyField('Recording')
    year = models.IntegerField(blank=True, null=True)
    label = models.ForeignKey('Label', blank=True, null=True)
    performance = models.ManyToManyField('Artist', through="InstrumentConcertPerformance")

    def length(self):
        tot_len = 0
        print "tracks"
        print self.tracks.all()
        for t in self.tracks.all():
            tot_len += t.length
            print t.length
        import time
        return time.strftime('%H:%M:%S', time.gmtime(tot_len))

    def __unicode__(self):
        ret = ", ".join([unicode(a) for a in self.artists.all()])
        if self.location:
            ret += " at " + unicode(self.location)
        return "%s (%s)" % (self.title, ret)

    def get_absolute_url(self):
        viewname = "%s-concert" % (self.get_style(), )
        return reverse(viewname, args=[str(self.id)])

    def get_image_url(self):
        media = settings.MEDIA_URL
        if self.images.all():
            image = self.images.all()[0]
            return os.path.join(media, image.image.name)
        else:
            return os.path.join(media, "missing", "concert.jpg")

    def get_musicbrainz_url(self):
        return "http://musicbrainz.org/release/%s" % self.mbid

    def artistnames(self):
        artists = self.artists.all()
        if len(artists) > 1:
            return artists
        elif len(artists) == 0:
            return None
        else:
            return artists[0]

    def performers(self):
        IPClass = self.get_object_map("performance")
        perf = IPClass.objects.filter(recording__in=self.tracks.all()).distinct().all()
        person = []
        ret = []
        # XXX: Do this as a group by query
        for p in perf:
            if p.performer.id not in person:
                person.append(p.performer.id)
                ret.append(p)
        return ret

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

    def get_musicbrainz_url(self):
        return "http://musicbrainz.org/work/%s" % self.mbid

    def concerts(self):
        ConcertClass = self.get_object_map("concert")
        return ConcertClass.objects.filter(tracks__work=self).all()

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

    def get_musicbrainz_url(self):
        return "http://musicbrainz.org/recording/%s" % self.mbid

    def all_artists(self):
        ArtistClass = self.get_object_map("artist")
        return ArtistClass.objects.filter(concert__tracks=self)

class InstrumentAlias(models.Model):
    class Meta:
        abstract = True
    name = models.CharField(max_length=50)
    instrument = models.ForeignKey("Instrument", related_name="aliases")

    def __unicode__(self):
        return self.name

class Instrument(BaseModel):
    class Meta:
        abstract = True
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

    def get_image_url(self):
        media = settings.MEDIA_URL
        if self.images.all():
            image = self.images.all()[0]
            return os.path.join(media, image.image.name)
        else:
            return os.path.join(media, "missing", "instrument.jpg")

    def get_absolute_url(self):
        viewname = "%s-instrument" % (self.get_style(), )
        return reverse(viewname, args=[str(self.id)])

    def artists(self):
        ArtistClass = self.get_object_map("artist")
        return ArtistClass.objects.filter(instrumentperformance__instrument=self).distinct().all()

class InstrumentConcertPerformance(models.Model):
    class Meta:
        abstract = True
    concert = models.ForeignKey('Concert')
    performer = models.ForeignKey('Artist')
    instrument = models.ForeignKey('Instrument')
    lead = models.BooleanField(default=False)

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
    begin = models.CharField(max_length=10, blank=True, null=True)
    end = models.CharField(max_length=10, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        viewname = "%s-composer" % (self.get_style(), )
        return reverse(viewname, args=[str(self.id)])

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

