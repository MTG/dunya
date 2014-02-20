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
from django.core.urlresolvers import reverse
from django.db.models import Q

import collections

import data.models

class HindustaniStyle(object):
    def get_style(self):
        return "hindustani"
    def get_object_map(self, key):
        return {"performance": InstrumentPerformance,
                "release": Release,
                "composer": Composer,
                "artist": Artist,
                "recording": Recording,
                "work": Work,
                "instrument": Instrument
                }[key]

class Instrument(HindustaniStyle, data.models.Instrument):
    pass

class Artist(HindustaniStyle, data.models.Artist):
    pass

class Release(HindustaniStyle, data.models.Release):
    pass

class RecordingRaag(models.Model):
    recording = models.ForeignKey("Recording")
    raag = models.ForeignKey("Raag")
    sequence = models.IntegerField()

class RecordingTaal(models.Model):
    recording = models.ForeignKey("Recording")
    taal = models.ForeignKey("Taal")
    laay = models.ForeignKey("Laay")
    sequence = models.IntegerField()

class RecordingSection(models.Model):
    recording = models.ForeignKey("Recording")
    section = models.ForeignKey("Section")
    sequence = models.IntegerField()

class RecordingForm(models.Model):
    recording = models.ForeignKey("Recording")
    form = models.ForeignKey("Form")
    sequence = models.IntegerField()

class Recording(HindustaniStyle, data.models.Recording):

    raags = models.ManyToManyField("Raag", through="RecordingRaag")
    taals = models.ManyToManyField("Taal", through="RecordingTaal")
    sections = models.ManyToManyField("Section", through="RecordingSection")
    forms = models.ManyToManyField("Form", through="RecordingForm")

class InstrumentPerformance(HindustaniStyle, data.models.InstrumentPerformance):
    pass

class Composer(HindustaniStyle, data.models.Composer):
    pass

class Lyrics(models.Model):
    lyrics = models.CharField(max_length=50)

class Work(models.Model):
    lyrics = models.ForeignKey("Lyrics")

class Section(models.Model):
    name = models.CharField(max_length=50)
    transliteration = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name.capitalize()

class Raag(models.Model):
    missing_image = "raag.jpg"

    name = models.CharField(max_length=50)
    transliteration = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name.capitalize()

    def get_absolute_url(self):
        return reverse('hindustani-raag', args=[str(self.id)])

class RaagAlias(models.Model):
    name = models.CharField(max_length=50)
    raag = models.ForeignKey("Raag", related_name="aliases")

    def __unicode__(self):
        return self.name

class Taal(models.Model):
    missing_image = "taal.jpg"

    name = models.CharField(max_length=50)
    transliteration = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name.capitalize()

    def get_absolute_url(self):
        return reverse('hindustani-taal', args=[str(self.id)])

class TaalAlias(models.Model):
    name = models.CharField(max_length=50)
    taal = models.ForeignKey("Taal", related_name="aliases")

    def __unicode__(self):
        return self.name

class Laay(models.Model):
    """ A laay is always referred to with a taal as well """
    missing_image = "laay.jpg"

    name = models.CharField(max_length=50)
    transliteration = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name.capitalize()

    def get_absolute_url(self):
        return reverse('hindustani-laay', args=[str(self.id)])

class LaayAlias(models.Model):
    name = models.CharField(max_length=50)
    laay = models.ForeignKey("Laay", related_name="aliases")

    def __unicode__(self):
        return self.name

class Form(models.Model):
    missing_image = "form.jpg"

    name = models.CharField(max_length=50)
    transliteration = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name.capitalize()

    def get_absolute_url(self):
        return reverse('hindustani-form', args=[str(self.id)])

class FormAlias(models.Model):
    name = models.CharField(max_length=50)
    form = models.ForeignKey("Form", related_name="aliases")

    def __unicode__(self):
        return self.name
