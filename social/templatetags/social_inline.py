from django import template
from django.conf import settings
from django.core.urlresolvers import reverse

from django.utils.http import urlquote, urlquote_plus

import collections

from carnatic.models import * # TODO: shouldn't be here

register = template.Library()

### SOCIAL PART ###
@register.simple_tag
def inline_user(user):
    if len(user.first_name) == 0:
        return '<a href="%s">%s</a>' % (reverse('social-user-page', args=[user.username]), user.username)
    else:
        return '<a href="%s">%s %s</a>' % (reverse('social-user-page', args=[user.username]), user.first_name, user.last_name)


@register.simple_tag
def inline_tag(tag):
    return '<a href="%s">%s</a>' % (reverse('social-tag-page', args=[urlquote_plus(tag["value"]), tag["content_type"]]), tag["value"])
    #return '<a href="%s">%s</a>' % (reverse('social-tag-page', args=[urlquote_plus(tag.tag_name), tag.modeltype]), tag.tag_name)
    

def reverse_comment(content_type, content_id):
    if content_type == "artist":
        artist = Artist.objects.get(pk=content_id)
        return artist.get_absolute_url()
    if content_type == "concert":
        concert = Concert.objects.get(pk=content_id)
        return concert.get_absolute_url()
    if content_type == "recording":
        recording = Recording.objects.get(pk=content_id)
        return recording.get_absolute_url()
    if content_type == "work":
        work = Work.objects.get(pk=content_id)
        return work.get_absolute_url()
    return None

@register.simple_tag
def inline_comment(comment):
    return '<a href="%s#c%s">comment</a>' % (reverse_comment(comment["content_type"], comment["content_id"]), comment["id"])