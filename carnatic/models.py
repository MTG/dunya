from django.db import models
from django.core.urlresolvers import reverse

import data.models
import managers

class CarnaticStyle(object):
    def get_style(self):
        return "carnatic"
    def get_object_map(self, key):
        return {"performance": InstrumentPerformance,
                "concert": Concert,
                "composer": Composer,
                "artist": Artist,
                "recording": Recording,
                "work": Work
                }[key]

class GeographicRegion(CarnaticStyle, models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

class MusicalSchool(CarnaticStyle, models.Model):
    name = models.CharField(max_length=100)

class Artist(CarnaticStyle, data.models.Artist):
    state = models.ForeignKey(GeographicRegion, blank=True, null=True)

class Sabbah(CarnaticStyle, models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

class Concert(CarnaticStyle, data.models.Concert):
    sabbah = models.ForeignKey(Sabbah, blank=True, null=True)

class RaagaAlias(models.Model):
    name = models.CharField(max_length=50)
    raaga = models.ForeignKey("Raaga", related_name="aliases")

    objects = managers.FuzzySearchManager()

    def __unicode__(self):
        return self.name

class Raaga(models.Model):
    name = models.CharField(max_length=50)

    objects = managers.FuzzySearchManager()

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('carnatic-raaga', args=[str(self.id)])

    def works(self):
        return self.work_set.all()

    def composers(self):
        return Composer.objects.filter(work__raaga=self)

    def artists(self):
        return Artist.objects.filter(concert__tracks__work__raaga=self)

class TaalaAlias(models.Model):
    name = models.CharField(max_length=50)
    taala = models.ForeignKey("Taala", related_name="aliases")

    objects = managers.FuzzySearchManager()

    def __unicode__(self):
        return self.name

class Taala(models.Model):
    name = models.CharField(max_length=50)

    objects = managers.FuzzySearchManager()

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('carnatic-taala', args=[str(self.id)])

    def works(self):
        return self.work_set.all()

    def composers(self):
        return Composer.objects.filter(work__taala=self)

    def artists(self):
        return Artist.objects.filter(concert__tracks__work__taala=self)

class Work(CarnaticStyle, data.models.Work):
    raaga = models.ManyToManyField('Raaga', through="WorkRaaga")
    taala = models.ManyToManyField('Taala', through="WorkTaala")
    #form = models.ForeignKey('Form', blank=True, null=True)

class WorkRaaga(models.Model):
    work = models.ForeignKey('Work')
    raaga = models.ForeignKey('Raaga')
    sequence = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return "%s, seq %d %s" % (self.work, self.sequence, self.raaga)

class WorkTaala(models.Model):
    work = models.ForeignKey('Work')
    taala = models.ForeignKey('Taala')
    sequence = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return "%s, seq %d %s" % (self.work, self.sequence, self.taala)

class WorkAttribute(CarnaticStyle, data.models.WorkAttribute):
    pass

class WorkAttributeType(CarnaticStyle, data.models.WorkAttributeType):
    pass

class WorkAttributeTypeValue(CarnaticStyle, data.models.WorkAttributeTypeValue):
    pass

class Recording(CarnaticStyle, data.models.Recording):
    pass

class InstrumentAlias(CarnaticStyle, data.models.InstrumentAlias):
    objects = managers.FuzzySearchManager()

class Instrument(CarnaticStyle, data.models.Instrument):
    objects = managers.FuzzySearchManager()

class InstrumentPerformance(CarnaticStyle, data.models.InstrumentPerformance):
    pass

class Composer(CarnaticStyle, data.models.Composer):
    state = models.ForeignKey(GeographicRegion, blank=True, null=True)
    def raagas(self):
        return Raaga.objects.filter(work__composer=self).all()

    def taalas(self):
        return Taala.objects.filter(work__composer=self).all()

class Location(CarnaticStyle, data.models.Location):
    pass

