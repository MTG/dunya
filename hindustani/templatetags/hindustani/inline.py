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
from django.utils.html import format_html, format_html_join, mark_safe

import collections
import hindustani

register = template.Library()

@register.simple_tag
def url_host_and_path(request, url):
    return request.build_absolute_uri(url)

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
        return mark_safe(u", ".join([inline_artist_part(a) for a in artists]))
    else:
        return u"(unknown)"


def inline_artist_part(artist):
    if isinstance(artist, hindustani.models.Artist):
        if artist.dummy:
            return format_html(u'<span class="title">{}</span>', artist.name)
        else:
            return format_html(u'<a href="{}" class="title">{}</a>', artist.get_absolute_url(), artist.name)
    else:
        return artist.name


@register.simple_tag
def inline_release(release, bold=False):
    sb = ""
    eb = ""
    if bold:
        sb = "<b>"
        eb = "</b>"
    return format_html(u'<a href="{}">%s{}%s</a>' % (sb, eb), release.get_absolute_url(), release.title)


@register.simple_tag
def inline_composer(composer):
    return format_html(u'<a href="{}">{}</a>', composer.get_absolute_url(), composer.name)


@register.simple_tag
def inline_recording(recording):
    return format_html(u'<a href="{}">{}</a>', recording.get_absolute_url(), recording.title)


@register.simple_tag
def inline_recording_artist(recording):
    if recording.artist() is not None:
        return recording.artist().name
    return "unknown"


@register.simple_tag
def inline_work_list(works):
    allworks = []
    for w in works:
        text = inline_work(w)
        if w.composers.exists():
            text = mark_safe(u"%s by %s" % (text, inline_composer(w.composers.all()[0])))
        allworks.append(text)
    return mark_safe(u", ".join(allworks))


@register.simple_tag
def inline_work(work):
    return work.title


@register.simple_tag
def inline_raag(raag):
    return format_html(u'<span title="{}">{}</span>', raag.common_name.title(), raag.name.title())


@register.simple_tag
def inline_laya(laya):
    return format_html(u'<span title="{}">{}</span>', laya.common_name.title(), laya.name.title())


@register.simple_tag
def inline_form(form):
    return format_html(u'<span title="{}">{}</span>', form.common_name.title(), form.name.title())


@register.simple_tag
def inline_taal(taal):
    return format_html(u'<span title="{}">{}</span>', taal.common_name.title(), taal.name.title())


@register.simple_tag
def inline_instrument(instrument):
    if not isinstance(instrument, collections.Iterable):
        instrument = [instrument]
    return format_html_join(u", ", u'<a href="{}">{}</a>', ((i.get_absolute_url(), i.name) for i in instrument if i))
