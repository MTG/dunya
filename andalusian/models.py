from django.db import models
from django_extensions.db.fields import UUIDField
from django.core.urlresolvers import reverse
from django.conf import settings

import os
import collections
import filters


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
        return u"From %s: %s (%s)" % (self.source_name, self.uri, self.last_updated)


class Description(models.Model):
    """ A short description of a thing in the database.
    It could be a biography, or a description """
    source = models.ForeignKey(Source, blank=True, null=True)
    description = models.TextField()

    def __unicode__(self):
        return u"%s - %s" % (self.source, self.description[:100])


class Image(models.Model):
    """ An image of a thing in the database """
    source = models.ForeignKey(Source, blank=True, null=True)
    image = models.ImageField(upload_to="images")
    small_image = models.ImageField(upload_to="images", blank=True, null=True)

    def __unicode__(self):
        ret = u"%s" % (self.image.name, )
        if self.source:
            ret = u"%s from %s" % (ret, self.source.uri)
        return ret


class BaseModel(models.Model):
    class Meta:
        abstract = True

    source = models.ForeignKey(Source, blank=True, null=True, related_name="%(app_label)s_%(class)s_source_set")
    references = models.ManyToManyField(Source, blank=True, null=True,
                                        related_name="%(app_label)s_%(class)s_reference_set")
    description = models.ForeignKey(Description, blank=True, null=True, related_name="+")
    images = models.ManyToManyField(Image, related_name="%(app_label)s_%(class)s_image_set")

    def ref(self):
        u = {"url": self.source.uri, "title": self.source.source_name.name}
        return u

    def get_image_url(self):
        media = settings.MEDIA_URL
        if self.images.all():
            image = self.images.all()[0]
            return os.path.join(media, image.image.name)
        else:
            if not hasattr(self, "missing_image"):
                missing_image = "artist.jpg"
            else:
                missing_image = self.missing_image
            return os.path.join(media, "missing", missing_image)

    def get_small_image_url(self):
        media = settings.MEDIA_URL
        if self.images.all():
            image = self.images.all()[0]
            if image.small_image:
                return os.path.join(media, image.small_image.name)
            else:
                return os.path.join(media, image.image.name)
        else:
            if not hasattr(self, "missing_image"):
                missing_image = "artist.jpg"
            else:
                missing_image = self.missing_image
            return os.path.join(media, "missing", missing_image)

    def get_style(self):
        raise Exception("need style")

    def get_object_map(self, key):
        raise Exception("need map")


class AndalusianStyle(object):

    def get_style(self):
        return "andalusian"

    def get_object_map(self, key):
        return {"performance": InstrumentPerformance,
                "release": Album,
                "artist": Artist,
                "instrument": Instrument,
                "sectionperformance": InstrumentSectionPerformance,
                "orchestraperformer": OrchestraPerformer,
                "recording": Recording,
                "orchestra": Orchestra,
                "section": Section
                }[key]


class MusicalSchool(AndalusianStyle, BaseModel):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class Orchestra(AndalusianStyle, BaseModel):
    mbid = UUIDField(blank=True, null=True)
    name = models.CharField(max_length=255)
    school = models.ForeignKey(MusicalSchool, blank=True, null=True)
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        viewname = "%s-orchestra" % (self.get_style(), )
        return reverse(viewname, args=[self.mbid])

    def get_musicbrainz_url(self):
        return "http://musicbrainz.org/artist/%s" % self.mbid

    def performers(self):
        IPClass = self.get_object_map("orchestraperformer")
        performances = IPClass.objects.filter(orchestra=self)
        perfs = [p.performer for p in performances]
        return perfs

    def recordings(self):
        return self.recording_set.all()


class OrchestraAlias(models.Model):
    name = models.CharField(max_length=255)
    orchestra = models.ForeignKey("Orchestra", related_name="aliases")
    
    def __unicode__(self):
        return self.name


class Artist(AndalusianStyle, BaseModel):
    missing_image = "artist.jpg"

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
        viewname = "%s-artist" % (self.get_style(), )
        return reverse(viewname, args=[self.mbid])
    
    def get_musicbrainz_url(self):
        return "http://musicbrainz.org/artist/%s" % self.mbid

    def recordings(self):
        IPClass = self.get_object_map("performance")
        performances = IPClass.objects.filter(performer=self)
        recs = [p.recording for p in performances]
        return recs
    
    def performances(self, tab=[], nawba=[], mizan=[]):
        pass
    
    def instruments(self):
        insts = []
        for perf in self.instrumentperformance_set.all():
            if perf.instrument.name not in insts:
                insts.append(perf.instrument)
        if len(insts) > 0:
            return insts[0]
        return None

    def similar_artists(self):
        pass

    def collaborating_artists(self):
        # Get all recordings
        # For each artist on the recordings (both types), add a counter
        # top 10 artist ids + the recordings they collaborate on
        c = collections.Counter()
        recordings = collections.defaultdict(set)
        for recording in self.recordings():
            for p in recording.performers():
                if p.id != self.id:
                    recordings[p.id].add(recording)
                    c[p.id] += 1
    
        return [(Artist.objects.get(pk=pk), list(recordings[pk])) for pk, count in c.most_common()]

    @classmethod
    def get_filter_criteria(cls):
        ret = {"url": reverse('andalusian-artist-search'),
               "name": "Artist",
               "data": [filters.School().object, filters.Generation().object]
        }
        return ret


class ArtistAlias(models.Model):
    name = models.CharField(max_length=200)
    artist = models.ForeignKey("Artist", related_name="aliases")
    
    def __unicode__(self):
        return self.name


class AlbumType(models.Model):
    type = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.type
    

class Album(AndalusianStyle, BaseModel):
    missing_image = "album.jpg"

    mbid = UUIDField(blank=True, null=True)
    title = models.CharField(max_length=255)
    album_type = models.ForeignKey(AlbumType, blank=True, null=True)

    def __unicode__(self):
        return self.title

    def recordings(self):
        return self.recording_set.all()

    def get_absolute_url(self):
        viewname = "%s-album" % (self.get_style(), )
        return reverse(viewname, args=[self.mbid])

    def get_musicbrainz_url(self):
        return "http://musicbrainz.org/release/%s" % self.mbid


class AlbumAlias(models.Model):
    title = models.CharField(max_length=255)
    album = models.ForeignKey("Album", related_name="aliases")
    
    def __unicode__(self):
        return self.title


class Recording(AndalusianStyle, BaseModel):
    mbid = UUIDField(blank=True, null=True)
    title = models.CharField(max_length=255)
    album = models.ForeignKey('Album')
    length = models.IntegerField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    genre = models.CharField(max_length=100)
    orchestra = models.ForeignKey('Orchestra')
    director = models.ForeignKey('Artist')

    def __unicode__(self):
        ret = u", ".join([unicode(a) for a in self.performers()])
        return u"%s (%s)" % (self.title, ret)

    def performers(self):
        performers = list(set([p.performer for p in self.instrumentperformance_set.all()]))
        return performers


class RecordingAlias(models.Model):
    title = models.CharField(max_length=255)
    recording = models.ForeignKey("Recording", related_name="aliases")
    
    def __unicode__(self):
        return self.title


class Instrument(AndalusianStyle, BaseModel):
    percussion = models.BooleanField(default=False)
    name = models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.name


class InstrumentAlias(models.Model):
    name = models.CharField(max_length=50)
    instrument = models.ForeignKey("Instrument", related_name="aliases")
    
    def __unicode__(self):
        return self.name


class InstrumentPerformance(models.Model):
    class Meta:        
        abstract = True
    recording = models.ForeignKey('Recording')
    performer = models.ForeignKey('Artist')
    instrument = models.ForeignKey('Instrument')
    lead = models.BooleanField(default=False)
    
    def __unicode__(self):
        return u"%s playing %s on %s" % (self.performer, self.instrument, self.recording)


class OrchestraPerformer(models.Model):
    orchestra = models.ForeignKey('Orchestra')
    performer = models.ForeignKey('Artist')
    instrument = models.ForeignKey('Instrument')
    director = models.BooleanField(default=False)
    begin = models.CharField(max_length=10, blank=True, null=True)
    end = models.CharField(max_length=10, blank=True, null=True)

    def __unicode__(self):
        ret = u"%s played %s on %s" % (self.performer, self.instrument, self.orchestra)
        if self.director:
            ret += u". Moreover, %s acted as the director of this orchestra" % self.performer
            if self.begin:
                ret += u" from %s" % self.begin
            if self.end:
                ret += u" until %s" % self.end
        return ret


class Tab(BaseModel):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name
    

class TabAlias(models.Model):
    name = models.CharField(max_length=50)
    tab = models.ForeignKey("Tab", related_name="aliases")
    
    def __unicode__(self):
        return self.name


class Nawba(BaseModel):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name
    

class NawbaAlias(models.Model):
    name = models.CharField(max_length=50)
    nawba = models.ForeignKey("Nawba", related_name="aliases")
    
    def __unicode__(self):
        return self.name
    

class Mizan(BaseModel):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name
    

class MizanAlias(models.Model):
    name = models.CharField(max_length=50)
    mizan = models.ForeignKey("Mizan", related_name="aliases")
    
    def __unicode__(self):
        return self.name
    

class FormType(models.Model):
    type = models.CharField(max_length=50)

    def __unicode__(self):
        return self.type
    

class Form(BaseModel):
    name = models.CharField(max_length=50)
    form_type = models.ForeignKey(FormType, blank=True, null=True)

    def __unicode__(self):
        return self.name
    

class FormAlias(models.Model):
    name = models.CharField(max_length=50)
    form = models.ForeignKey("Form", related_name="aliases")
    
    def __unicode__(self):
        return self.name
    

class Section(AndalusianStyle, BaseModel):
    recording = models.ForeignKey('Recording')
    # order_number may not be necessary if start_time and end_time are known
    order_number = models.IntegerField(blank=True, null=True)
    start_time = models.CharField(max_length=8, blank=True, null=True)
    end_time = models.CharField(max_length=8, blank=True, null=True)
    tab = models.ForeignKey('Tab', blank=True, null=True)
    nawba = models.ForeignKey('Nawba', blank=True, null=True)
    mizan = models.ForeignKey('Mizan', blank=True, null=True)
    form = models.ForeignKey('Form', blank=True, null=True)

    def __unicode__(self):
        return u"Section %s of %s (from %s to %s), a %s from mizan %s of tab' %s, nawba %s" % \
               (self.order_number, self.recording, self.start_time, self.end_time,
                self.form, self.mizan, self.tab, self.nawba)
    

class InstrumentSectionPerformance(models.Model):
    section = models.ForeignKey('Section')
    performer = models.ForeignKey('Artist')
    instrument = models.ForeignKey('Instrument')
    lead = models.BooleanField(default=False)

    def __unicode__(self):
        return u"%s playing %s on section %s of recording %s" % \
               (self.performer, self.instrument, self.section.order_number, self.section.recording)


class Sanaa(BaseModel):
    title = models.CharField(max_length=255)

    def __unicode__(self):
        return self.title
    

class SanaaAlias(models.Model):
    title = models.CharField(max_length=255)
    sanaa = models.ForeignKey("Sanaa", related_name="aliases")

    def __unicode__(self):
        return self.title


class PoemType(models.Model):
    type = models.CharField(max_length=50)

    def __unicode__(self):
        return self.type


class Poem(BaseModel):
    identifier = models.CharField(max_length=100, blank=True, null=True)
    first_words = models.CharField(max_length=255, blank=True, null=True)
    type = models.ForeignKey(PoemType, blank=True, null=True)
    text = models.TextField()

    def __unicode__(self):
        return self.identifier
    

class PoemAlias(models.Model):
    identifier = models.CharField(max_length=100, blank=True, null=True)
    poem = models.ForeignKey("Poem", related_name="aliases")

    def __unicode__(self):
        return self.identifier
    

class SectionSanaaPoem(models.Model):
    section = models.ForeignKey('Section')
    sanaa = models.ForeignKey('Sanaa')
    poem = models.ForeignKey('Poem')
    order_number = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return u"Poem %s from san'a %s in section %s of recording %s" % \
               (self.poem, self.sanaa, self.section.order_number, self.section.recording)
