from django import template
from django.conf import settings
from django.core.urlresolvers import reverse

import collections
import carnatic

register = template.Library()

@register.simple_tag
def url_host_and_path(request, url):
    return request.build_absolute_uri(url)

@register.simple_tag
def inline_artist(artist):
    return inline_artist_part(artist)

@register.simple_tag
def inline_artist_list(artists):
    artists = list(artists)
    if len(artists) > 1:
        firsts = artists[:-1]
        last = artists[-1]
        firsturls = [inline_artist_part(a) for a in firsts]
        lasturl = inline_artist_part(last)
        firststr = ", ".join(firsturls)
        return "%s & %s" % (firststr, lasturl)
    else:
        if len(artists):
            return inline_artist_part(artists[0])
        else:
            return "(unknown)"

def inline_artist_part(artist):
    if isinstance(artist, carnatic.models.Artist):
        return '<a href="%s">%s</a>' % (artist.get_absolute_url(), artist.name)
    else:
        return ""

@register.simple_tag
def inline_concert(concert, bold=False):
    sb = ""
    eb = ""
    if bold:
        sb = "<b>"
        eb = "</b>"
    return '<a href="%s">%s%s%s</a>' % (concert.get_absolute_url(), sb, concert.title, eb)

@register.simple_tag
def inline_composer(composer):
    return composer.name
    return '<a href="%s">%s</a>' % (composer.get_absolute_url(), composer.name)

@register.simple_tag
def inline_recording(recording):
    return '<a href="%s">%s</a>' % (recording.get_absolute_url(), recording.title)

@register.simple_tag
def inline_recording_artist(recording):
    if recording.artist() is not None:
        return recording.artist().name
    return "unknown"

@register.simple_tag
def inline_work(work):
    # TODO: Disable work links for now
    return work.title
    #return '<a href="%s">%s</a>' % (work.get_absolute_url(), work.title)

@register.simple_tag
def inline_raaga(raaga):
    return '<a href="%s">%s</a>' % (raaga.get_absolute_url(), raaga.name.title())

@register.simple_tag
def inline_taala(taala):
    return '<a href="%s">%s</a>' % (taala.get_absolute_url(), taala.name.title())

@register.simple_tag
def inline_instrument(instrument):
    if not isinstance(instrument, collections.Iterable):
        instrument = [instrument]
    ret = []
    for i in instrument:
        if i:
            ret.append('<a href="%s">%s</a>' % (i.get_absolute_url(), i.name))
    return ", ".join(ret)
