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

from django import template

from carnatic import models

register = template.Library()


#### Badges for the front page

@register.inclusion_tag("carnatic/badges/concert.html")
def badge_concert(concert):
    if not isinstance(concert, models.Concert):
        concert = models.Concert.objects.get(pk=concert)
    return {"concert": concert}

@register.inclusion_tag("carnatic/badges/performance.html")
def badge_performance(concert, artist):
    instruments = concert.instruments_for_artist(artist)
    return {"instruments": instruments, "artist": artist}

@register.inclusion_tag("carnatic/badges/artist.html")
def badge_artist(artist):
    if not isinstance(artist, models.Artist):
        artist = models.Artist.objects.get(pk=artist)
    return {"artist": artist}

@register.inclusion_tag("carnatic/badges/recording.html")
def badge_recording(recording):
    return {"recording": recording}

@register.inclusion_tag("carnatic/badges/instrument.html")
def badge_instrument(instrument):
    if not isinstance(instrument, models.Instrument):
        instrument = models.Instrument.objects.get(pk=instrument)
    return {"instrument": instrument}

@register.inclusion_tag("carnatic/badges/raaga.html")
def badge_raaga(raaga):
    if not isinstance(raaga, models.Raaga):
        raaga = models.Raaga.objects.get(pk=raaga)
    return {"raaga": raaga}

@register.inclusion_tag("carnatic/badges/taala.html")
def badge_taala(taala):
    if not isinstance(taala, models.Taala):
        taala = models.Taala.objects.get(pk=taala)
    return {"taala": taala}

@register.inclusion_tag("carnatic/badges/composer.html")
def badge_composer(composer):
    if not isinstance(composer, models.Composer):
        composer = models.Composer.objects.get(pk=composer)
    return {"composer": composer}

@register.inclusion_tag("carnatic/badges/work.html")
def badge_work(work):
    if not isinstance(work, models.Work):
        work = models.Work.objects.get(pk=work)
    return {"work": work}

#### Badges for comparing an item to other things of the same type

@register.inclusion_tag("carnatic/badges/similar_artist.html")
def badge_similar_artist(artist, concerts=None, bootlegs=None, guru=None, description=False):
    if not isinstance(artist, models.Artist):
        artist = models.Artist.objects.get(pk=artist)
    return {"artist": artist,
            "concerts": concerts,
            "guru": guru,
            "bootlegs": bootlegs,
            "description": description}

@register.inclusion_tag("carnatic/badges/similar_concert.html")
def badge_similar_concert(concert, similarity):
    if not isinstance(concert, models.Concert):
        concert = models.Concert.objects.get(pk=concert)
    return {"concert": concert,
            "works": similarity.get("works", []),
            "taalas": similarity.get("taalas", []),
            "raagas": similarity.get("raagas", []),
            "artists": similarity.get("artists", []),
            }

@register.inclusion_tag("carnatic/badges/similar_raaga.html")
def badge_similar_raaga(raaga):
    return {"raaga": raaga}

@register.inclusion_tag("carnatic/badges/similar_recording.html")
def badge_similar_recording(recording):
    return {"recording": recording}

#### Detail badges (for showing on the detail page of another item)

@register.inclusion_tag("carnatic/badges/detail_concert.html")
def badge_detail_concert(concert):
    if not isinstance(concert, models.Concert):
        concert = models.Concert.objects.get(pk=concert)
    return {"concert": concert}

@register.inclusion_tag("carnatic/badges/detail_artist.html")
def badge_detail_artist(artist):
    return {"artist": artist}

@register.inclusion_tag("carnatic/badges/detail_work.html", takes_context=True)
def badge_detail_work(context, work):
    return {"work": work, "request": context["request"]}

#### Mini badges (for inside badges)

@register.inclusion_tag("carnatic/badges/mini_concert.html")
def badge_mini_concert(concert):
    return {"concert": concert}

@register.inclusion_tag("carnatic/badges/mini_performance.html")
def badge_mini_performance(performance):
    # TODO: Coordinate types?
    """ Performance could be an instrumentperf or an instrumentconcertperf"""
    return {"performance": performance}

@register.inclusion_tag("carnatic/badges/mini_artist.html")
def badge_mini_artist(artist):
    return {"artist": artist}

@register.inclusion_tag("carnatic/badges/mini_recording.html")
def badge_mini_recording(recording):
    if not isinstance(recording, models.Recording):
        recording = models.Recording.objects.get(pk=recording)
    return {"recording": recording}

@register.inclusion_tag("carnatic/badges/mini_instrument.html")
def badge_mini_instrument(instrument):
    if not isinstance(instrument, models.Instrument):
        instrument = models.Instrument.objects.get(pk=instrument)
    return {"instrument": instrument}

@register.inclusion_tag("carnatic/badges/mini_raaga.html")
def badge_mini_raaga(raaga):
    if not isinstance(raaga, models.Raaga):
        raaga = models.Raaga.objects.get(pk=raaga)
    return {"raaga": raaga}

@register.inclusion_tag("carnatic/badges/mini_taala.html")
def badge_mini_taala(taala):
    if not isinstance(taala, models.Taala):
        taala = models.Taala.objects.get(pk=taala)
    return {"taala": taala}

@register.inclusion_tag("carnatic/badges/mini_composer.html")
def badge_mini_composer(composer):
    if not isinstance(composer, models.Composer):
        composer = models.Composer.objects.get(pk=composer)
    return {"composer": composer}

@register.inclusion_tag("carnatic/badges/mini_work.html")
def badge_mini_work(work):
    if not isinstance(work, models.Work):
        work = models.Work.objects.get(pk=work)
    return {"work": work}

@register.inclusion_tag("carnatic/badges/sample.html")
def badge_sample(sample):
    return {"sample": sample}

@register.inclusion_tag("carnatic/badges/reference.html")
def badge_reference(reference):
    return {"reference": reference}

#### Micro badges (for inside badges)

@register.inclusion_tag("carnatic/badges/micro_artist.html")
def badge_micro_artist(artist):
    return {"artist": artist}

@register.inclusion_tag("carnatic/badges/micro_concert.html")
def badge_micro_concert(concert):
    return {"concert": concert}

@register.inclusion_tag("carnatic/badges/micro_instrument.html")
def badge_micro_instrument(instrument):
    return {"instrument": instrument}

@register.inclusion_tag("carnatic/badges/micro_taala.html")
def badge_micro_taala(taala):
    return {"taala": taala}

@register.inclusion_tag("carnatic/badges/micro_raaga.html")
def badge_micro_raaga(raaga):
    return {"raaga": raaga}
