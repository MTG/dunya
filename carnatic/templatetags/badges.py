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
           }

@register.inclusion_tag("badges/artist.html")
def badge_performance(performance):
    if not isinstance(performance, InstrumentPerformance):
        performance = InstrumentPerformance.objects.get(pk=performance)
    return {"performance": performance
           }

@register.inclusion_tag("badges/recording.html")
def badge_recording(recording):
    if not isinstance(recording, Recording):
        recording = Recording.objects.get(pk=recording)
    return {"recording": recording
           }
