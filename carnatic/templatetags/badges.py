from django import template

from carnatic.models import *

register = template.Library()


#### Badges for the front page

@register.inclusion_tag("badges/concert.html")
def badge_concert(concert):
    if not isinstance(concert, Concert):
        concert = Concert.objects.get(pk=concert)
    return {"concert": concert}

@register.inclusion_tag("badges/performance.html")
def badge_performance(performance):
    artist = performance.performer
    return {"performance": performance, "artist": artist}

@register.inclusion_tag("badges/artist.html")
def badge_artist(artist):
    if not isinstance(artist, Artist):
        artist = Artist.objects.get(pk=artist)
    return {"artist": artist}

@register.inclusion_tag("badges/recording.html")
def badge_recording(recording):
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

#### Badges for comparing an item to other things of the same type

@register.inclusion_tag("badges/similar_artist.html")
def badge_similar_artist(artist, concerts=None, guru=None):
    if not isinstance(artist, Artist):
        artist = Artist.objects.get(pk=artist)
    return {"artist": artist, "concerts":concerts, "guru": guru}

@register.inclusion_tag("badges/similar_concert.html")
def badge_similar_concert(concert, similarity):
    print "in concert similarity. sim object is"
    print similarity
    if not isinstance(concert, Concert):
        concert = Concert.objects.get(pk=concert)
    return {"concert": concert,
            "works": similarity.get("works", []),
            "taalas": similarity.get("taalas", []),
            "raagas": similarity.get("raagas", []),
            "artists": similarity.get("artists", []),
            }

@register.inclusion_tag("badges/similar_raaga.html")
def badge_similar_raaga(raaga):
    return {"raaga": raaga}

@register.inclusion_tag("badges/similar_recording.html")
def badge_similar_recording(recording):
    return {"recording": recording}

#### Detail badges (for showing on the detail page of another item)

@register.inclusion_tag("badges/detail_concert.html")
def badge_detail_concert(concert):
    if not isinstance(concert, Concert):
        concert = Concert.objects.get(pk=concert)
    return {"concert": concert}

@register.inclusion_tag("badges/detail_artist.html")
def badge_detail_artist(artist):
    print "detail badge artist", artist
    return {"artist": artist}

#### Mini badges (for inside badges)

@register.inclusion_tag("badges/mini_concert.html")
def badge_mini_concert(concert):
    return {"concert": concert}

@register.inclusion_tag("badges/mini_performance.html")
def badge_mini_performance(performance):
    # TODO: Coordinate types?
    """ Performance could be an instrumentperf or an instrumentconcertperf"""
    return {"performance": performance}

@register.inclusion_tag("badges/mini_artist.html")
def badge_mini_artist(artist):
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
