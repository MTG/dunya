from django import template

from carnatic.models import *

register = template.Library()

@register.inclusion_tag("badges/similar_concert.html")
def badge_similar_concert(concert):
    if not isinstance(concert, Concert):
        concert = Concert.objects.get(pk=concert)
    return {"concert": concert}

@register.inclusion_tag("badges/concert.html")
def badge_concert(concert):
    if not isinstance(concert, Concert):
        concert = Concert.objects.get(pk=concert)
    return {"concert": concert}

@register.inclusion_tag("badges/artist.html")
def badge_performance(performance):
    if not isinstance(performance, InstrumentPerformance):
        performance = InstrumentPerformance.objects.get(pk=performance)
    return {"performance": performance}

@register.inclusion_tag("badges/artist.html")
def badge_artist(artist):
    if not isinstance(artist, Artist):
        artist = Artist.objects.get(pk=artist)
    return {"artist": artist}

@register.inclusion_tag("badges/recording.html")
def badge_recording(recording):
    if not isinstance(recording, Recording):
        recording = Recording.objects.get(pk=recording)
    return {"recording": recording}

@register.inclusion_tag("badges/instrument.html")
def badge_instrument(instrument):
    if not isinstance(instrument, Instrument):
        instrument = Instrument.objects.get(pk=instrument)
    return {"instrument": instrument}

@register.inclusion_tag("badges/sample.html")
def badge_sample(sample):
    return {"sample": sample}

@register.inclusion_tag("badges/reference.html")
def badge_reference(reference):
    return {"reference": reference}
