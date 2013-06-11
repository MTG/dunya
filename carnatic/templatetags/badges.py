from django import template

from carnatic.models import *

register = template.Library()

@register.inclusion_tag("badges/album.html")
def badge_concert(concert):
    if not isinstance(concert, Concert):
        concert = Concert.objects.get(pk=concert)
    return {"title": concert.title,
            "artists": concert.artistnames(),
            "detail": None,
            "date": 2043,
            "url": concert.get_absolute_url()
           }

@register.inclusion_tag("badges/artist.html")
def badge_performance(performance):
    if not isinstance(performance, InstrumentPerformance):
        performance = InstrumentPerformance.objects.get(pk=performance)
    return {"performance": performance
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
    return {"performance": performance
           }

@register.inclusion_tag("badges/recording.html")
def badge_recording(recording):
    if not isinstance(recording, Recording):
        recording = Recording.objects.get(pk=recording)
    return {"recording": recording
           }

@register.inclusion_tag("badges/sample.html")
def badge_sample(sample):
    return {"sample": sample}

@register.inclusion_tag("badges/reference.html")
def badge_reference(reference):
    return {"reference": reference}
