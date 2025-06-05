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

import math
import os
import time

import unidecode
from django.conf import settings
from django.contrib.sites.models import Site
from django.urls import reverse
from django.db import models
from django.utils.text import slugify

import docserver


class ClassProperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


class SourceName(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Source(models.Model):
    # The source type that we got this data from (wikipedia, musicbrainz, etc)
    source_name = models.ForeignKey(SourceName, on_delete=models.CASCADE)
    # The title of the page on the source website
    title = models.CharField(max_length=255)
    # The URL of the source
    uri = models.CharField(max_length=255)
    last_updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.source_name}: {self.uri} ({self.last_updated})"


class Description(models.Model):
    """A short description of a thing in the database.
    It could be a biography, or a description"""

    source = models.ForeignKey(Source, blank=True, null=True, on_delete=models.CASCADE)
    description = models.TextField()

    def __str__(self):
        return f"{self.source} - {self.description[:100]}"


class Image(models.Model):
    """An image of a thing in the database"""

    source = models.ForeignKey(Source, blank=True, null=True, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="images")
    small_image = models.ImageField(upload_to="images", blank=True, null=True)

    def __str__(self):
        ret = f"{self.image.name}"
        if self.source:
            ret = f"{ret} from {self.source.uri}"
        return ret


class ImageMixin(object):
    def has_image(self):
        return self.image is not None

    def get_image_url(self):
        media = settings.MEDIA_URL
        if self.has_image():
            return os.path.join(media, self.image.image.name)
        else:
            missing_image = getattr(self, "missing_image", "artist.jpg")
            return os.path.join(media, "missing", missing_image)

    def get_small_image_url(self):
        media = settings.MEDIA_URL
        if self.has_image():
            if self.image.small_image:
                return os.path.join(media, self.image.small_image.name)
            else:
                return os.path.join(media, self.image.image.name)
        else:
            missing_image = getattr(self, "missing_image", "artist.jpg")
            return os.path.join(media, "missing", missing_image)


class BaseModel(models.Model):
    class Meta:
        abstract = True

    def get_style(self):
        raise Exception("need style")

    def get_object_map(self, key):
        raise Exception("need map")


class Artist(BaseModel, ImageMixin):
    missing_image = "artist.jpg"

    class Meta:
        abstract = True

    GENDER_CHOICES = (("M", "Male"), ("F", "Female"))
    TYPE_CHOICES = (("P", "Person"), ("G", "Group"))
    name = models.CharField(max_length=200)
    mbid = models.UUIDField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    begin = models.CharField(max_length=10, blank=True, null=True)
    end = models.CharField(max_length=10, blank=True, null=True)
    artist_type = models.CharField(max_length=1, choices=TYPE_CHOICES, default="P")
    main_instrument = models.ForeignKey("Instrument", blank=True, null=True, on_delete=models.CASCADE)
    group_members = models.ManyToManyField("Artist", blank=True, related_name="groups")
    dummy = models.BooleanField(default=False, db_index=True)
    image = models.ForeignKey(
        Image, blank=True, null=True, related_name="%(app_label)s_%(class)s_image", on_delete=models.CASCADE
    )

    description = models.ForeignKey(Description, blank=True, null=True, related_name="+", on_delete=models.CASCADE)
    description_edited = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        viewname = f"{self.get_style()}-artist"
        if isinstance(self.name, unicode):
            aname = unidecode.unidecode(self.name)
        else:
            aname = self.name
        return reverse(viewname, args=[str(self.mbid), slugify(aname)])

    def get_musicbrainz_url(self):
        return f"http://musicbrainz.org/artist/{self.mbid}"

    def instruments(self):
        InstrumentKlass = self.get_object_map("instrument")
        return InstrumentKlass.objects.filter(instrumentperformance__artist=self).distinct()


class ArtistAlias(models.Model):
    class Meta:
        abstract = True

    artist = models.ForeignKey("Artist", related_name="aliases", on_delete=models.CASCADE)
    alias = models.CharField(max_length=100)
    primary = models.BooleanField(default=False)
    locale = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.alias} (alias for {self.artist})"


class Release(BaseModel, ImageMixin):
    missing_image = "concert.jpg"

    class Meta:
        abstract = True

    mbid = models.UUIDField(blank=True, null=True)
    title = models.CharField(max_length=100)
    # Main artists on the concert
    artists = models.ManyToManyField("Artist", related_name="primary_concerts")
    artistcredit = models.CharField(max_length=255)
    year = models.IntegerField(blank=True, null=True)
    image = models.ForeignKey(
        Image, blank=True, null=True, related_name="%(app_label)s_%(class)s_image", on_delete=models.CASCADE
    )

    status = models.CharField(max_length=100, blank=True, null=True)
    rel_type = models.CharField(max_length=100, blank=True, null=True)
    # These fields are specified on the concrete model classes because they might use
    # different spellings (Release/Concert)
    # Ordered tracks
    # tracks = models.ManyToManyField('Recording', through="ReleaseRecording")

    def length(self):
        tot_len = 0
        for t in self.recordings.all():
            tot_len += t.length / 1000
        return time.strftime("%H:%M:%S", time.gmtime(tot_len))

    def __str__(self):
        ret = ", ".join([str(a) for a in self.artists.all()])
        return f"{self.title} ({ret})"

    def get_absolute_url(self):
        viewname = f"{self.get_style()}-release"
        return reverse(viewname, args=[str(self.mbid), slugify(self.title)])

    def get_musicbrainz_url(self):
        return f"http://musicbrainz.org/release/{self.mbid}"

    def artistnames(self):
        return self.artists.all()


class Collection(models.Model):
    class Meta:
        permissions = (("access_restricted", "Can see restricted collections"),)

    PERMISSIONS = (("S", "Staff-only"), ("R", "Restricted"), ("U", "Unrestricted"))

    collectionid = models.UUIDField()
    permission = models.CharField(max_length=1, choices=PERMISSIONS, default="S")
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"data/{self.name}[{self.collectionid}] ({self.permission})"


class Work(BaseModel):
    class Meta:
        abstract = True

    title = models.CharField(max_length=100)
    mbid = models.UUIDField(blank=True, null=True)
    composers = models.ManyToManyField("Composer", blank=True, related_name="works")
    lyricists = models.ManyToManyField("Composer", blank=True, related_name="lyric_works")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        viewname = f"{self.get_style()}-work"
        return reverse(viewname, args=[str(self.mbid), slugify(self.title)])

    def get_musicbrainz_url(self):
        return f"http://musicbrainz.org/work/{self.mbid}"

    def artists(self):
        ArtistClass = self.get_object_map("artist")
        return ArtistClass.objects.filter(primary_concerts__recordings__work=self).distinct()


class Recording(BaseModel):
    class Meta:
        abstract = True

    title = models.CharField(max_length=200)
    mbid = models.UUIDField(blank=True, null=True)
    length = models.IntegerField(blank=True, null=True)
    performance = models.ManyToManyField("Artist", through="InstrumentPerformance")

    # On concrete class because a recording may have >1 work in some styles
    # work = models.ForeignKey('Work', blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        viewname = f"{self.get_style()}-recording"
        return reverse(viewname, args=[str(self.mbid), slugify(self.title)])

    def get_musicbrainz_url(self):
        return f"http://musicbrainz.org/recording/{self.mbid}"

    def absolute_mp3_url(self):
        try:
            url = docserver.util.docserver_get_mp3_url(self.mbid)
        except docserver.exceptions.NoFileException:
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
        except docserver.exceptions.NoFileException:
            try:
                return docserver.util.docserver_get_url(self.mbid, "audioimages", "waveform32", 1)
            except docserver.exceptions.NoFileException:
                return ""


class InstrumentAlias(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=50)
    instrument = models.ForeignKey("Instrument", related_name="aliases", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Instrument(BaseModel, ImageMixin):
    class Meta:
        abstract = True

    missing_image = "instrument.jpg"

    percussion = models.BooleanField(default=False)
    name = models.CharField(max_length=50)
    # Instruments have mbids too
    mbid = models.UUIDField(blank=True, null=True)
    image = models.ForeignKey(
        Image, blank=True, null=True, related_name="%(app_label)s_%(class)s_image", on_delete=models.CASCADE
    )

    description = models.ForeignKey(Description, blank=True, null=True, related_name="+", on_delete=models.CASCADE)

    # Some instruments exist because they have relationships, but we
    # don't want to show them
    hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        viewname = f"{self.get_style()}-instrument"
        return reverse(viewname, args=[str(self.mbid), slugify(self.name)])

    def artists(self):
        ArtistClass = self.get_object_map("artist")
        return ArtistClass.objects.filter(instrumentperformance__instrument=self).distinct().all()


class InstrumentPerformance(models.Model):
    class Meta:
        abstract = True

    recording = models.ForeignKey("Recording", on_delete=models.CASCADE)
    artist = models.ForeignKey("Artist", on_delete=models.CASCADE)
    instrument = models.ForeignKey("Instrument", blank=True, null=True, on_delete=models.CASCADE)
    lead = models.BooleanField(default=False)
    attributes = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        person = f"{self.artist}"
        if self.instrument:
            person += f" playing {self.instrument}"
        person += f" on {self.recording}"
        return person


class Composer(BaseModel, ImageMixin):
    missing_image = "artist.jpg"

    class Meta:
        abstract = True

    GENDER_CHOICES = (("M", "Male"), ("F", "Female"))
    name = models.CharField(max_length=200)
    mbid = models.UUIDField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    begin = models.CharField(max_length=10, blank=True, null=True)
    end = models.CharField(max_length=10, blank=True, null=True)

    image = models.ForeignKey(
        Image, blank=True, null=True, related_name="%(app_label)s_%(class)s_image", on_delete=models.CASCADE
    )
    description = models.ForeignKey(Description, blank=True, null=True, related_name="+", on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_musicbrainz_url(self):
        return f"http://musicbrainz.org/composer/{self.mbid}"

    def get_absolute_url(self):
        viewname = f"{self.get_style()}-composer"
        if isinstance(self.name, unicode):
            cname = unidecode.unidecode(self.name)
        else:
            cname = self.name
        args = [self.mbid]
        slug = slugify(cname)
        if slug:
            args.append(slug)
        return reverse(viewname, args=args)


class ComposerAlias(models.Model):
    class Meta:
        abstract = True

    composer = models.ForeignKey("Composer", related_name="aliases", on_delete=models.CASCADE)
    alias = models.CharField(max_length=100)
    primary = models.BooleanField(default=False)
    locale = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.alias} (alias for {self.composer})"


# This mixin needs to be used with ModelSerializable
# to generate the image absolute url
class WithImageMixin(object):
    def get_image_abs_url(self, ob):
        str_ret = "http://"
        request = self.context.get("request", None)
        if request and request.is_secure():
            str_ret = "https://"
        current_site = Site.objects.get_current()
        return str_ret + current_site.domain + ob.get_image_url()
