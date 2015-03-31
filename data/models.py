# Copyright 2013,2014 Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of Dunya
#
# Dunya is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation (FSF), either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/

from django.db import models
from django_extensions.db.fields import UUIDField
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.text import slugify
from django.contrib.sites.models import Site


import docserver

import os
import time
import math
import unidecode

class ClassProperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()

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
    references = models.ManyToManyField(Source, blank=True, related_name="%(app_label)s_%(class)s_reference_set")
    description = models.ForeignKey(Description, blank=True, null=True, related_name="+")
    images = models.ManyToManyField(Image, related_name="%(app_label)s_%(class)s_image_set")

    def refs(self):
        ret = []
        ret.append({"url": self.source.uri, "title": self.source.source_name.name})
        for r in self.references.all():
            ret.append({"url": r.uri, "title": r.source_name.name})
        return ret

    def has_image(self):
        return bool(self.images.count())

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

class Artist(BaseModel):
    missing_image = "artist.jpg"

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
    group_members = models.ManyToManyField('Artist', blank=True, related_name='groups')
    dummy = models.BooleanField(default=False, db_index=True)
    description_edited = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        viewname = "%s-artist" % (self.get_style(), )
        if isinstance(self.name, unicode):
            aname = unidecode.unidecode(self.name)
        else:
            aname = self.name
        return reverse(viewname, args=[self.mbid, slugify(unicode(aname))])

    def get_musicbrainz_url(self):
        return "http://musicbrainz.org/artist/%s" % self.mbid

    def instruments(self):
        InstrumentKlass = self.get_object_map("instrument")
        return InstrumentKlass.objects.filter(instrumentperformance__artist=self).distinct()


class ArtistAlias(models.Model):
    class Meta:
        abstract = True
    artist = models.ForeignKey("Artist", related_name="aliases")
    alias = models.CharField(max_length=100)
    primary = models.BooleanField(default=False)
    locale = models.CharField(max_length=10, blank=True, null=True)

    def __unicode__(self):
        return u"%s (alias for %s)" % (self.alias, self.artist)

class Release(BaseModel):
    missing_image = "concert.jpg"

    class Meta:
        abstract = True
    mbid = UUIDField(blank=True, null=True)
    title = models.CharField(max_length=100)
    # Main artists on the concert
    artists = models.ManyToManyField('Artist', related_name='primary_concerts')
    artistcredit = models.CharField(max_length=255)
    year = models.IntegerField(blank=True, null=True)

    # These fields are specified on the concrete model classes because they might use
    # different spellings (Release/Concert)
    # Ordered tracks
    # tracks = models.ManyToManyField('Recording', through="ReleaseRecording")

    def length(self):
        tot_len = 0
        for t in self.recordings.all():
            tot_len += t.length / 1000
        return time.strftime('%H:%M:%S', time.gmtime(tot_len))

    def __unicode__(self):
        ret = u", ".join([unicode(a) for a in self.artists.all()])
        return u"%s (%s)" % (self.title, ret)

    def get_absolute_url(self):
        viewname = "%s-release" % (self.get_style(), )
        return reverse(viewname, args=[self.mbid, slugify(self.title)])

    def get_musicbrainz_url(self):
        return "http://musicbrainz.org/release/%s" % self.mbid

    def artistnames(self):
        return self.artists.all()

class Work(BaseModel):
    class Meta:
        abstract = True
    title = models.CharField(max_length=100)
    mbid = UUIDField(blank=True, null=True)
    composers = models.ManyToManyField('Composer', blank=True, related_name="works")
    lyricists = models.ManyToManyField('Composer', blank=True, related_name="lyric_works")

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        viewname = "%s-work" % (self.get_style(), )
        return reverse(viewname, args=[self.mbid, slugify(self.title)])

    def get_musicbrainz_url(self):
        return "http://musicbrainz.org/work/%s" % self.mbid

    def artists(self):
        ArtistClass = self.get_object_map("artist")
        return ArtistClass.objects.filter(primary_concerts__recordings__work=self).distinct()

class Recording(BaseModel):
    class Meta:
        abstract = True
    title = models.CharField(max_length=200)
    mbid = UUIDField(blank=True, null=True)
    length = models.IntegerField(blank=True, null=True)
    performance = models.ManyToManyField('Artist', through="InstrumentPerformance")

    # On concrete class because a recording may have >1 work in some styles
    # work = models.ForeignKey('Work', blank=True, null=True)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        viewname = "%s-recording" % (self.get_style(), )
        return reverse(viewname, args=[self.mbid, slugify(self.title)])

    def get_musicbrainz_url(self):
        return "http://musicbrainz.org/recording/%s" % self.mbid

    def absolute_mp3_url(self):
        try:
            url = docserver.util.docserver_get_mp3_url(self.mbid)
        except docserver.util.NoFileException:
            url = None
        return url

    def length_format(self):
        numsecs = self.length / 1000
        minutes = math.floor(numsecs / 60.0)
        hours = math.floor(minutes / 60.0)
        minutes = math.floor(minutes - hours * 60)
        seconds = math.floor(numsecs - hours * 3600 - minutes * 60)
        if hours:
            val = "%02d:%02d:%02d" % (hours, minutes, seconds)
        else:
            val = "%02d:%02d" % (minutes, seconds)

        return val

    def length_seconds(self):
        return self.length / 1000

    def all_artists(self):
        ArtistClass = self.get_object_map("artist")
        primary_artists = ArtistClass.objects.filter(primary_concerts__recordings=self)

        IPClass = self.get_object_map("performance")
        recperfs = IPClass.objects.filter(recording=self)
        rec_artists = [r.artist for r in recperfs]

        all_as = set(primary_artists) | set(rec_artists)
        return list(all_as)

    def waveform_image(self):
        # TODO: Select this image in a better way, or show a better
        # representation
        try:
            # we return "4", because it might be more interesting than 1, but if it fails
            # (e.g. only 3?) then just return 1
            return docserver.util.docserver_get_url(self.mbid, "audioimages", "waveform32", 4)
        except docserver.util.NoFileException:
            try:
                return docserver.util.docserver_get_url(self.mbid, "audioimages", "waveform32", 1)
            except docserver.util.NoFileException:
                return ""


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
    missing_image = "instrument.jpg"

    percussion = models.BooleanField(default=False)
    name = models.CharField(max_length=50)
    # Instruments have mbids too
    mbid = UUIDField(blank=True, null=True)

    # Some instruments exist because they have relationships, but we
    # don't want to show them
    hidden = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        viewname = "%s-instrument" % (self.get_style(), )
        return reverse(viewname, args=[str(self.mbid), slugify(self.name)])

    def artists(self):
        ArtistClass = self.get_object_map("artist")
        return ArtistClass.objects.filter(instrumentperformance__instrument=self).distinct().all()

class InstrumentPerformance(models.Model):
    class Meta:
        abstract = True
    recording = models.ForeignKey('Recording')
    artist = models.ForeignKey('Artist')
    instrument = models.ForeignKey('Instrument', blank=True, null=True)
    lead = models.BooleanField(default=False)

    def __unicode__(self):
        person = u"%s" % self.artist
        if self.instrument:
            person += u" playing %s" % self.instrument
        person += u" on %s" % self.recording
        return person

class Composer(BaseModel):
    missing_image = "artist.jpg"

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

    def get_musicbrainz_url(self):
        return "http://musicbrainz.org/composer/%s" % self.mbid

    def get_absolute_url(self):
        viewname = "%s-composer" % (self.get_style(), )
        if isinstance(self.name, unicode):
            cname = unidecode.unidecode(self.name)
        else:
            cname = self.name
        args = [self.mbid]
        slug = slugify(unicode(cname))
        if slug:
            args.append(slug)
        return reverse(viewname, args=args)

class ComposerAlias(models.Model):
    class Meta:
        abstract = True
    composer = models.ForeignKey("Composer", related_name="aliases")
    alias = models.CharField(max_length=100)
    primary = models.BooleanField(default=False)
    locale = models.CharField(max_length=10, blank=True, null=True)

    def __unicode__(self):
        return u"%s (alias for %s)" % (self.alias, self.composer)

class VisitLog(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    user = models.CharField(max_length=100, blank=True, null=True)
    # ipv4 only!
    ip = models.CharField(max_length=16)
    path = models.CharField(max_length=256)

    def __unicode__(self):
        return u"%s: (%s/%s): %s" % (self.date, self.user, self.ip, self.path)

# This mixin needs to be used with ModelSerializable
# to generate the image absolute url
class WithImageMixin(object):
    def get_image_abs_url(self, ob):
        str_ret = 'http://'
        request = self.context.get('request', None)
        if request and request.is_secure():
            str_ret = 'https://'
        current_site = Site.objects.get_current()
        return str_ret + current_site.domain + ob.get_image_url()
