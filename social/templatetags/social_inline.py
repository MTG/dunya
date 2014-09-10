# Copyright 2013,2014 Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of Dunya
#
# Dunya is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation (FSF), either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/

from django import template
from django.core.urlresolvers import reverse

from django.utils.http import urlquote_plus

from carnatic import models

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
        artist = models.Artist.objects.get(pk=content_id)
        return artist.get_absolute_url()
    if content_type == "concert":
        concert = models.Concert.objects.get(pk=content_id)
        return concert.get_absolute_url()
    if content_type == "recording":
        recording = models.Recording.objects.get(pk=content_id)
        return recording.get_absolute_url()
    if content_type == "work":
        work = models.Work.objects.get(pk=content_id)
        return work.get_absolute_url()
    return None

@register.simple_tag
def inline_comment(comment):
    return '<a href="%s#c%s">comment</a>' % (reverse_comment(comment["content_type"], comment["content_id"]), comment["id"])
