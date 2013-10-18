from django import template

from carnatic.models import *

register = template.Library()

def get_image(entity, noimage):
    if entity.images.count():
        image = entity.images.all()[0].image.url
    else:
        image = "/media/images/%s.jpg" % noimage
    return image


@register.inclusion_tag("badges/similar_concert.html")
def badge_similar_concert(concert):
    if not isinstance(concert, Concert):
        concert = Concert.objects.get(pk=concert)
    return {"title": concert.title,
            "artist": concert.artistnames(),
            "detail": None,
            "date": concert.year,
            "url": concert.get_absolute_url(),
            "image": get_image(concert, "noconcert")
           }

@register.inclusion_tag("badges/concert.html")
def badge_concert(concert):
    if not isinstance(concert, Concert):
        concert = Concert.objects.get(pk=concert)
    return {"concert": concert
           }

@register.inclusion_tag("badges/artist.html")
def badge_performance(performance):
    if not isinstance(performance, InstrumentPerformance):
        performance = InstrumentPerformance.objects.get(pk=performance)
    artist = performance.performer
    if artist.images.count():
        image = artist.images.all()[0].image.url
    else:
        image = "/media/images/noartist.jpg"
    return {"performance": performance,
            "image": image
           }

@register.inclusion_tag("badges/artist.html")
def badge_artist(artist):
    if not isinstance(artist, Artist):
        artist = Artist.objects.get(pk=artist)
    perfs = artist.instrumentperformance_set.all()
    if perfs:
        performance = perfs[0]
    else:
        performance = None
    return {"artist": artist
           }

@register.inclusion_tag("badges/recording.html")
def badge_recording(recording):
    if not isinstance(recording, Recording):
        recording = Recording.objects.get(pk=recording)
    return {"recording": recording
           }

@register.inclusion_tag("badges/instrument.html")
def badge_instrument(instrument):
    if not isinstance(instrument, Instrument):
        instrument = Instrument.objects.get(pk=instrument)
    return {"instrument": instrument,
            "image": get_image(instrument, "noinstrument")
           }


@register.inclusion_tag("badges/sample.html")
def badge_sample(sample):
    return {"sample": sample}

@register.inclusion_tag("badges/reference.html")
def badge_reference(reference):
    return {"reference": reference}
