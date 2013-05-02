from django import template

from carnatic.models import *

register = template.Library()

@register.inclusion_tag("badges/album.html")
def badge_concert(concert):
    if not isinstance(concert, Concert):
        concert = Concert.objects.get(pk=concert)
    artists = ", ".join([a.name for a in concert.performers()])
    return {"title": concert.title,
            "artists": artists,
            "detail": None,
            "date": None,
           }

@register.inclusion_tag("badges/artist.html")
def badge_performance(performance):
    if not isinstance(performance, InstrumentPerformance):
        performance = InstrumentPerformance.objects.get(pk=performance)
    return {"name": performance.performer.name,
            "instrument": performance.instrument.name,
           }
