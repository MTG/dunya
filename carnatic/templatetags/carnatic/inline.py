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

import collections

from django import template
from django.utils.html import format_html, format_html_join, mark_safe

import carnatic

register = template.Library()


@register.simple_tag
def inline_artist(artist):
    if artist:
        return inline_artist_part(artist)
    else:
        return ""


@register.simple_tag
def inline_artist_list(artists):
    artists = list(artists)
    if len(artists) == 1:
        return inline_artist_part(artists[0])
    elif len(artists) > 1:
        return mark_safe(", ".join([inline_artist_part(a) for a in artists]))
    else:
        return "(unknown)"


def inline_artist_part(artist):
    if isinstance(artist, carnatic.models.Artist):
        return format_html('<span class="title">{}</span>', artist.name)
    else:
        return artist.name


@register.simple_tag
def inline_concert(concert, bold=False):
    sb = ""
    eb = ""
    if bold:
        sb = "<b>"
        eb = "</b>"
    return format_html('<span>{}{{}}{}</span>'.format(sb, eb), concert.title)


@register.simple_tag
def inline_composer(composer):
    return format_html('<span>{}</span>', composer.name)


@register.simple_tag
def inline_work(work):
    return work.title


@register.simple_tag
def inline_raaga(raaga):
    if raaga:
        return format_html('<span title="{}">{}</span>', raaga.common_name.title(), raaga.name.title())
    else:
        return '(unknown)'


@register.simple_tag
def inline_taala(taala):
    if taala:
        return format_html('<span title="{}">{}</span>', taala.common_name.title(), taala.name.title())
    else:
        return '(unknown)'
