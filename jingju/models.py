from django.db import models

import data.models
from jingju import managers


class JingjuStyle:
    def get_style(self):
        return "jingju"

    def get_object_map(self, key):
        return {
            "performance": RecordingInstrumentalist,
            "release": Release,
            "artist": Artist,
            "recording": Recording,
            "work": Work,
            "instrument": Instrument,
        }[key]


class Recording(JingjuStyle, data.models.BaseModel):
    class Meta:
        ordering = ["id"]

    title = models.CharField(max_length=200, blank=True, null=True)
    mbid = models.UUIDField(blank=True, null=True)
    work = models.ForeignKey("Work", null=True, on_delete=models.CASCADE)
    performers = models.ManyToManyField("Artist")
    instrumentalists = models.ManyToManyField(
        "Artist", through="RecordingInstrumentalist", related_name="instrumentalist"
    )
    shengqiangbanshi = models.ManyToManyField("ShengqiangBanshi")
    objects = managers.CollectionRecordingManager()

    def __str__(self):
        return f"{self.title}"


class RecordingInstrumentalist(JingjuStyle, models.Model):
    recording = models.ForeignKey("Recording", on_delete=models.CASCADE)
    artist = models.ForeignKey("Artist", on_delete=models.CASCADE)
    instrument = models.ForeignKey("Instrument", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.recording} - {self.artist} - {self.instrument}"


class Artist(data.models.Artist):
    romanisation = models.CharField(max_length=200, blank=True, null=True)
    role_type = models.ForeignKey("RoleType", blank=True, null=True, on_delete=models.CASCADE)
    instrument = models.ForeignKey("Instrument", blank=True, null=True, related_name="jingju", on_delete=models.CASCADE)
    objects = managers.ArtistManager()

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.name} ({self.romanisation})"


class Composer(data.models.Composer):
    alias = models.CharField(max_length=200, blank=True, null=True)
    objects = managers.ArtistManager()

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.name}"


class Instrument(data.models.Instrument):
    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.name}"


class RecordingRelease(models.Model):
    recording = models.ForeignKey("Recording", on_delete=models.CASCADE)
    release = models.ForeignKey("Release", on_delete=models.CASCADE)
    sequence = models.IntegerField(blank=True, null=True)

    # The number that the track comes in the concert. Numerical 1-n
    track = models.IntegerField(blank=True, null=True)
    # The disc number. 1-n
    disc = models.IntegerField(blank=True, null=True)
    # The track number within this disc. 1-n
    disctrack = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ("track",)

    def __str__(self):
        return f"{self.track}: {self.recording} from {self.release}"


class Work(JingjuStyle, data.models.Work):
    class Meta:
        ordering = ["id"]

    title = models.CharField(max_length=200, blank=True, null=True)
    mbid = models.UUIDField(blank=True, null=True)
    score = models.ForeignKey("Score", blank=True, null=True, on_delete=models.CASCADE)
    play = models.ForeignKey("Play", blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title}"


class Release(JingjuStyle, data.models.Release):
    class Meta:
        ordering = ["id"]

    recordings = models.ManyToManyField("Recording", through="RecordingRelease")
    collection = models.ForeignKey("data.Collection", blank=True, null=True, on_delete=models.CASCADE)
    objects = managers.CollectionReleaseManager()

    def __str__(self):
        return f"{self.title}"


class RoleType(data.models.BaseModel):
    class Meta:
        ordering = ["code"]

    # The code used in tags in musicbrainz to identify this roletype (hd00)
    # the first digit specifies a "parent" roletype, and the second digit a subtype.
    code = models.CharField(max_length=10, db_index=True)
    name = models.CharField(max_length=100)
    romanisation = models.CharField(max_length=100)
    uuid = models.UUIDField()

    # The "main" roletype for a more specific one. An artist who performs in a specific roletype
    # by definition performs in the parent roletype
    parent = models.ForeignKey("RoleType", blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.code}: {self.name}/{self.romanisation}"


class Play(data.models.BaseModel):
    title = models.CharField(max_length=100)
    uuid = models.UUIDField(blank=True, null=True)


class Score(data.models.BaseModel):
    # the name of the work
    name = models.CharField(max_length=100)
    # The name of the series
    source = models.CharField(max_length=100)
    # read this from the annotation of the series (we need to make it machine readable)
    citation = models.CharField(max_length=100, blank=True, null=True)
    citation_romanisation = models.CharField(max_length=100, blank=True, null=True)

    # This shouldn't be a uuidfield (
    uuid = models.UUIDField(blank=True, null=True)

    def __str__(self):
        return f"{self.name}"


class ShengqiangBanshi(data.models.BaseModel):
    # The code used in tags in musicbrainz to identify this shengqiangbanshi (sqbs000)
    code = models.CharField(max_length=10, db_index=True, unique=True)
    name = models.CharField(max_length=100)
    romanisation = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.code}: {self.name}/{self.romanisation}"
