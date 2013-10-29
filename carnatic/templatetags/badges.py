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

@register.inclusion_tag("badges/performance.html")
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

@register.inclusion_tag("badges/raaga.html")
def badge_raaga(raaga):
    if not isinstance(raaga, Raaga):
        raaga = Raaga.objects.get(pk=raaga)
    return {"raaga": raaga}

@register.inclusion_tag("badges/taala.html")
def badge_taala(taala):
    if not isinstance(taala, Taala):
        taala = Taala.objects.get(pk=taala)
    return {"taala": taala}

@register.inclusion_tag("badges/composer.html")
def badge_composer(composer):
    if not isinstance(composer, Composer):
        composer = Composer.objects.get(pk=composer)
    return {"composer": composer}

@register.inclusion_tag("badges/work.html")
def badge_work(work):
    if not isinstance(work, Work):
        work = Work.objects.get(pk=work)
    return {"work": work}

#### Mini badges

@register.inclusion_tag("badges/mini_concert.html")
def badge_mini_concert(concert):
    if not isinstance(concert, Concert):
        concert = Concert.objects.get(pk=concert)
    return {"concert": concert}

@register.inclusion_tag("badges/mini_performance.html")
def badge_mini_performance(performance):
    if not isinstance(performance, InstrumentPerformance):
        performance = InstrumentPerformance.objects.get(pk=performance)
    return {"performance": performance}

@register.inclusion_tag("badges/mini_artist.html")
def badge_mini_artist(artist):
    if not isinstance(artist, Artist):
        artist = Artist.objects.get(pk=artist)
    return {"artist": artist}

@register.inclusion_tag("badges/mini_recording.html")
def badge_mini_recording(recording):
    if not isinstance(recording, Recording):
        recording = Recording.objects.get(pk=recording)
    return {"recording": recording}

@register.inclusion_tag("badges/mini_instrument.html")
def badge_mini_instrument(instrument):
    if not isinstance(instrument, Instrument):
        instrument = Instrument.objects.get(pk=instrument)
    return {"instrument": instrument}

@register.inclusion_tag("badges/mini_raaga.html")
def badge_mini_raaga(raaga):
    if not isinstance(raaga, Raaga):
        raaga = Raaga.objects.get(pk=raaga)
    return {"raaga": raaga}

@register.inclusion_tag("badges/mini_taala.html")
def badge_mini_taala(taala):
    if not isinstance(taala, Taala):
        taala = Taala.objects.get(pk=taala)
    return {"taala": taala}

@register.inclusion_tag("badges/mini_composer.html")
def badge_mini_composer(composer):
    if not isinstance(composer, Composer):
        composer = Composer.objects.get(pk=composer)
    return {"composer": composer}

@register.inclusion_tag("badges/mini_work.html")
def badge_mini_work(work):
    if not isinstance(work, Work):
        work = Work.objects.get(pk=work)
    return {"work": work}

@register.inclusion_tag("badges/sample.html")
def badge_sample(sample):
    return {"sample": sample}

@register.inclusion_tag("badges/reference.html")
def badge_reference(reference):
    return {"reference": reference}
