from django.db import models
from django.urls import reverse


class MotifManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().using("motif")


class File(models.Model):
    objects = MotifManager()

    filename = models.CharField(max_length=1000)
    mbid = models.UUIDField(blank=True, null=True)
    hasseed = models.IntegerField()

    def __str__(self):
        return f"{self.filename} ({self.mbid}) [{self.hasseed}]"


class Match(models.Model):
    objects = MotifManager()

    source = models.ForeignKey("Pattern", related_name="match_sources", on_delete=models.CASCADE)
    target = models.ForeignKey("Pattern", related_name="match_targets", on_delete=models.CASCADE)
    distance = models.FloatField()
    version = models.IntegerField()

    def __str__(self):
        return f"{self.source}, {self.target} ({self.distance}) [{self.version}]"


class Pattern(models.Model):
    objects = MotifManager()

    file = models.ForeignKey(File, on_delete=models.CASCADE)
    start_time = models.FloatField()
    end_time = models.FloatField()
    pair_id = models.IntegerField(blank=True, null=True)  # ForeignKey to Pattern
    isseed = models.IntegerField()
    segment = models.ForeignKey("Segment", related_name="patterns", blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return "File {} ({} - {}) [{}, {}]".format(
            self.file.mbid, self.start_time, self.end_time, self.isseed, self.pair_id
        )


class Segment(models.Model):
    objects = MotifManager()

    file = models.ForeignKey(File, on_delete=models.CASCADE)
    rounded_start = models.FloatField()
    rounded_end = models.FloatField()
    segment_path = models.CharField(max_length=500)

    def __str__(self):
        return f"segment of {self.file} ({self.rounded_start}-{self.rounded_end})"

    def get_absolute_url(self):
        return reverse("motif-segment", args=[self.pk])
