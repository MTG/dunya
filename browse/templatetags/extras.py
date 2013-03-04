from django import template
from django.conf import settings
from data.models import *

register = template.Library()

@register.simple_tag
def inline_artist(artist):
    if not isinstance(artist, Artist):
        artist = Artist.objects.get(pk=artist)
    return '<a href="%s">%s</a>' % (artist.get_absolute_url(), artist.name)

@register.simple_tag
def inline_concert(concert):
    if not isinstance(concert, Concert):
        concert = Concert.objects.get(pk=concert)
    return '<a href="%s">%s</a>' % (concert.get_absolute_url(), concert.title)

@register.simple_tag
def inline_composer(composer):
    if not isinstance(composer, Composer):
        composer = Composer.objects.get(pk=composer)
    return '<a href="%s">%s</a>' % (composer.get_absolute_url(), composer.name)

@register.simple_tag
def inline_recording(recording):
    if not isinstance(recording, Recording):
        recording = Recording.objects.get(pk=recording)
    return '<a href="%s">%s</a>' % (recording.get_absolute_url(), recording.title)

@register.simple_tag
def inline_raaga(raaga):
    if not isinstance(raaga, Raaga):
        raaga = Raaga.objects.get(pk=raaga)
    return '<a href="%s">%s</a>' % (raaga.get_absolute_url(), raaga.name)

@register.simple_tag
def inline_taala(taala):
    if not isinstance(taala, Taala):
        taala = Taala.objects.get(pk=taala)
    return '<a href="%s">%s</a>' % (taala.get_absolute_url(), taala.name)

@register.simple_tag
def inline_instrument(instrument):
    if not isinstance(instrument, Instrument):
        instrument = Instrument.objects.get(pk=instrument)
    return '<a href="%s">%s</a>' % (instrument.get_absolute_url(), instrument.name)
