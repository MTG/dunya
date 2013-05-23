from django import template
from django.conf import settings
from django.core.urlresolvers import reverse

import collections

register = template.Library()

@register.simple_tag
def inline_artist(artist):
    return '<a href="%s">%s</a>' % (artist.get_absolute_url(), artist.name)

@register.simple_tag
def inline_concert(concert):
    return '<a href="%s">%s</a>' % (concert.get_absolute_url(), concert.title)

@register.simple_tag
def inline_composer(composer):
    return '<a href="%s">%s</a>' % (composer.get_absolute_url(), composer.name)

@register.simple_tag
def inline_recording(recording):
    return '<a href="%s">%s</a>' % (recording.get_absolute_url(), recording.title)

@register.simple_tag
def inline_work(work):
    return '<a href="%s">%s</a>' % (work.get_absolute_url(), work.title)

@register.simple_tag
def inline_raaga(raaga):
    return '<a href="%s">%s</a>' % (raaga.get_absolute_url(), raaga.name)

@register.simple_tag
def inline_taala(taala):
    return '<a href="%s">%s</a>' % (taala.get_absolute_url(), taala.name)

@register.simple_tag
def inline_instrument(instrument):
    if not isinstance(instrument, collections.Iterable):
        instrument = [instrument]
    ret = []
    for i in instrument:
        ret.append('<a href="%s">%s</a>' % (i.get_absolute_url(), i.name))
    return ", ".join(ret)

### SOCIAL PART ###
@register.simple_tag
def inline_user(user):
    if len(user.first_name) == 0:
        return '<a href="%s">%s</a>' % (reverse('social-user-page', args=[user.username]), user.username)
    else:
        return '<a href="%s">%s %s</a>' % (reverse('social-user-page', args=[user.username]), user.first_name, user.last_name)
