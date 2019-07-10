import collections

import math
from django.db import models
from django.urls import reverse

import data.models


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


class MusicalSchool(AndalusianStyle, data.models.BaseModel):
    name = models.CharField(max_length=100)
    transliterated_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class Orchestra(AndalusianStyle, data.models.BaseModel):
    class Meta:
        ordering = ['id']

    mbid = models.UUIDField(blank=True, null=True)
    name = models.CharField(max_length=255)
    transliterated_name = models.CharField(max_length=255, blank=True)
    school = models.ForeignKey(MusicalSchool, blank=True, null=True, on_delete=models.CASCADE)
    group_members = models.ManyToManyField('Artist', blank=True, related_name='groups', through="OrchestraPerformer")

    def __str__(self):
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
    orchestra = models.ForeignKey("Orchestra", related_name="aliases", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Artist(AndalusianStyle, data.models.BaseModel):
    class Meta:
        ordering = ['id']

    missing_image = "artist.jpg"

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female')
    )
    name = models.CharField(max_length=200)
    transliterated_name = models.CharField(max_length=200, blank=True)
    mbid = models.UUIDField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    begin = models.CharField(max_length=10, blank=True, null=True)
    end = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
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


class ArtistAlias(data.models.ArtistAlias):
    pass


class AlbumType(models.Model):
    type = models.CharField(max_length=255)
    transliterated_type = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.type


class AlbumRecording(models.Model):
    """ Links a album to a recording with an explicit ordering """
    album = models.ForeignKey('Album', on_delete=models.CASCADE)
    recording = models.ForeignKey('Recording', on_delete=models.CASCADE)
    # The number that the track comes in the album. Numerical 1-n
    track = models.IntegerField()

    class Meta:
        ordering = ("track", )

    def __str__(self):
        return u"%s: %s from %s" % (self.track, self.recording, self.album)


class Album(AndalusianStyle, data.models.BaseModel):
    class Meta:
        ordering = ['id']

    missing_image = "album.jpg"

    mbid = models.UUIDField(blank=True, null=True)
    title = models.CharField(max_length=255)
    transliterated_title = models.CharField(max_length=255, blank=True)
    album_type = models.ForeignKey(AlbumType, blank=True, null=True, on_delete=models.CASCADE)
    artists = models.ManyToManyField('Orchestra')
    recordings = models.ManyToManyField('Recording', through="AlbumRecording")
    director = models.ForeignKey('Artist', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        viewname = "%s-album" % (self.get_style(), )
        return reverse(viewname, args=[self.mbid])

    def get_musicbrainz_url(self):
        return "http://musicbrainz.org/release/%s" % self.mbid


class Work(AndalusianStyle, data.models.BaseModel):
    class Meta:
        ordering = ['id']

    mbid = models.UUIDField(blank=True, null=True)
    title = models.CharField(max_length=255)
    transliterated_title = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title


class Genre(AndalusianStyle, data.models.BaseModel):
    class Meta:
        ordering = ['id']

    name = models.CharField(max_length=100, blank=True)
    transliterated_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class RecordingWork(models.Model):
    work = models.ForeignKey('Work', on_delete=models.CASCADE)
    recording = models.ForeignKey('Recording', on_delete=models.CASCADE)
    sequence = models.IntegerField()

    class Meta:
        ordering = ("sequence", )

    def __str__(self):
        return u"%s: %s" % (self.sequence, self.work.title)


class Recording(AndalusianStyle, data.models.BaseModel):
    class Meta:
        ordering = ['id']

    mbid = models.UUIDField(blank=True, null=True)
    works = models.ManyToManyField("Work", through="RecordingWork")
    artists = models.ManyToManyField("Artist", through="InstrumentPerformance")
    title = models.CharField(max_length=255)
    transliterated_title = models.CharField(max_length=255, blank=True)
    length = models.IntegerField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    genre = models.ForeignKey('Genre', null=True, on_delete=models.CASCADE)
    archive_url = models.CharField(max_length=255)
    musescore_url = models.CharField(max_length=255)
    poems = models.ManyToManyField("Poem", through="RecordingPoem")

    def __str__(self):
        return u"%s" % self.title

    def performers(self):
        return self.artists.all()

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

    def get_dict(self):
        release = self.album_set.first()
        title = None
        if release:
            title = release.title
        image = "/media/images/noconcert.jpg"
        artists = self.artists.values_list('name').all()[:3]
        return {
                "concert": title,
                "mainArtists": [item for sublist in artists for item in sublist],
                "name": self.title,
                "image": image,
                "linkToRecording": reverse("andalusian-recording", args=[self.mbid]),
                "collaborators": [],
                "selectedArtists": ""
        }


class Instrument(AndalusianStyle, data.models.BaseModel):
    class Meta:
        ordering = ['id']

    percussion = models.BooleanField(default=False)
    name = models.CharField(max_length=50)
    mbid = models.UUIDField(blank=True, null=True)

    def __str__(self):
        return self.name


class InstrumentPerformance(models.Model):
    recording = models.ForeignKey('Recording', on_delete=models.CASCADE)
    performer = models.ForeignKey('Artist', on_delete=models.CASCADE)
    instrument = models.ForeignKey('Instrument', on_delete=models.CASCADE)
    lead = models.BooleanField(default=False)

    def __str__(self):
        return u"%s playing %s on %s" % (self.performer, self.instrument, self.recording)


class OrchestraPerformer(models.Model):
    orchestra = models.ForeignKey('Orchestra', on_delete=models.CASCADE)
    performer = models.ForeignKey('Artist', on_delete=models.CASCADE)
    instruments = models.ManyToManyField('Instrument')
    director = models.BooleanField(default=False)
    begin = models.CharField(max_length=10, blank=True, null=True)
    end = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        ret = u"%s played %s on %s" % (self.performer, u", ".join([str(i) for i in self.instruments.all()]), self.orchestra)
        if self.director:
            ret += u". Moreover, %s acted as the director of this orchestra" % self.performer
            if self.begin:
                ret += u" from %s" % self.begin
            if self.end:
                ret += u" until %s" % self.end
        return ret


class Tab(data.models.BaseModel):
    class Meta:
        ordering = ['display_order', 'id']

    uuid = models.UUIDField(db_index=True, null=True)
    name = models.CharField(max_length=50)
    transliterated_name = models.CharField(max_length=50, blank=True)

    # Set to 1 to force some Tab to show at the bottom when listing them
    display_order = models.IntegerField(null=False, default=0)

    def __str__(self):
        return self.name


class Nawba(data.models.BaseModel):
    class Meta:
        ordering = ['display_order', 'id']

    uuid = models.UUIDField(db_index=True, null=True)
    name = models.CharField(max_length=50, blank=True)
    transliterated_name = models.CharField(max_length=50, blank=True)

    # Set to 1 to force some Nawba to show at the bottom when listing them
    display_order = models.IntegerField(null=False, default=0)

    def __str__(self):
        return self.name


class Mizan(data.models.BaseModel):
    class Meta:
        ordering = ['display_order', 'id']

    uuid = models.UUIDField(db_index=True, null=True)
    name = models.CharField(max_length=50, blank=True)
    transliterated_name = models.CharField(max_length=50, blank=True)

    # Set to 1 to force some Mizan to show at the bottom when listing them
    display_order = models.IntegerField(null=False, default=0)

    def __str__(self):
        return self.name


class FormType(models.Model):
    type = models.CharField(max_length=50)

    def __str__(self):
        return self.type


class Form(data.models.BaseModel):
    class Meta:
        ordering = ['display_order', 'id']

    uuid = models.UUIDField(db_index=True, null=True)
    name = models.CharField(max_length=50)
    transliterated_name = models.CharField(max_length=50, blank=True)
    form_type = models.ForeignKey(FormType, blank=True, null=True, on_delete=models.CASCADE)

    # Set to 1 to force some Form to show at the bottom when listing them
    display_order = models.IntegerField(null=False, default=0)

    def __str__(self):
        return self.name


class Section(AndalusianStyle, data.models.BaseModel):
    recording = models.ForeignKey('Recording', on_delete=models.CASCADE)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    tab = models.ForeignKey('Tab', blank=True, null=True, on_delete=models.CASCADE)
    nawba = models.ForeignKey('Nawba', blank=True, null=True, on_delete=models.CASCADE)
    mizan = models.ForeignKey('Mizan', blank=True, null=True, on_delete=models.CASCADE)
    form = models.ForeignKey('Form', blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return u"Section of %s (from %s to %s), a %s from mizan %s of tab' %s, nawba %s" % \
               (self.recording, self.start_time, self.end_time,
                self.form, self.mizan, self.tab, self.nawba)


class InstrumentSectionPerformance(models.Model):
    section = models.ForeignKey('Section', on_delete=models.CASCADE)
    performer = models.ForeignKey('Artist', on_delete=models.CASCADE)
    instrument = models.ForeignKey('Instrument', on_delete=models.CASCADE)
    lead = models.BooleanField(default=False)

    def __str__(self):
        return u"%s playing %s on section (%s, %s) of recording %s" % \
               (self.performer, self.instrument, self.section.start_time, self.section.end_time, self.section.recording)


class Sanaa(data.models.BaseModel):
    class Meta:
        ordering = ['id']

    title = models.CharField(max_length=255)
    transliterated_title = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title


class PoemType(models.Model):
    type = models.CharField(max_length=50)

    def __str__(self):
        return self.type


class Poem(data.models.BaseModel):
    class Meta:
        ordering = ['id']

    identifier = models.CharField(max_length=100, blank=True, null=True)
    first_words = models.CharField(max_length=255, blank=True, null=True)
    transliterated_first_words = models.CharField(max_length=255, blank=True, null=True)
    type = models.ForeignKey(PoemType, blank=True, null=True, on_delete=models.CASCADE)
    text = models.TextField()
    transliterated_text = models.TextField(blank=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    transliterated_title = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.identifier


class RecordingPoem(models.Model):
    recording = models.ForeignKey('Recording', on_delete=models.CASCADE)
    poem = models.ForeignKey('Poem', on_delete=models.CASCADE)
    order_number = models.IntegerField(blank=True, null=True)
