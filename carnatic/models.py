from django.db import models
from django.core.urlresolvers import reverse

import data.models

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

class Artist(CarnaticStyle, data.models.Artist):
    pass

class Concert(CarnaticStyle, data.models.Concert):
    pass

class Raaga(models.Model):
    name = models.CharField(max_length=50)

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

class Taala(models.Model):
    name = models.CharField(max_length=20)

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
    raaga = models.ForeignKey('Raaga', blank=True, null=True)
    taala = models.ForeignKey('Taala', blank=True, null=True)
    #form = models.ForeignKey('Form', blank=True, null=True)

class WorkAttribute(CarnaticStyle, data.models.WorkAttribute):
    pass

class WorkAttributeType(CarnaticStyle, data.models.WorkAttributeType):
    pass

class WorkAttributeTypeValue(CarnaticStyle, data.models.WorkAttributeTypeValue):
    pass

class Recording(CarnaticStyle, data.models.Recording):
    pass

class Instrument(CarnaticStyle, data.models.Instrument):
    pass

class InstrumentPerformance(CarnaticStyle, data.models.InstrumentPerformance):
    pass

class Composer(CarnaticStyle, data.models.Composer):
    def raagas(self):
        return Raaga.objects.filter(work__composer=self).all()

    def taalas(self):
        return Taala.objects.filter(work__composer=self).all()

class Location(CarnaticStyle, data.models.Location):
    pass

