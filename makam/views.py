# -*- coding: UTF-8 -*-

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

from django.shortcuts import render, get_object_or_404, redirect

from makam import models

# Simple player for Georgi/Istanbul musicians
def makamplayer(request):
    return render(request, "makam/makamplayer.html")

def main(request):
    return render(request, "makam/index.html", {})

def composer(request, uuid):
    composer = get_object_or_404(models.Composer, mbid=uuid)

    ret = {"composer": composer
          }
    return render(request, "makam/composer.html", ret)

def artist(request, uuid):
    artist = get_object_or_404(models.Artist, mbid=uuid)

    ret = {"artist": artist
          }
    return render(request, "makam/artist.html", ret)

def release(request, uuid):
    release = get_object_or_404(models.Release, mbid=uuid)

    ret = {"release": release
          }
    return render(request, "makam/release.html", ret)

def recording(request, uuid):
    recording = get_object_or_404(models.Recording, mbid=uuid)

    ret = {"recording": recording
          }
    return render(request, "makam/recording.html", ret)

def work(request, uuid):
    work = get_object_or_404(models.Work, mbid=uuid)

    ret = {"work": work
          }
    return render(request, "makam/work.html", ret)

def makam(request, makamid):
    makam = get_object_or_404(models.Makam, pk=makamid)

    ret = {"makam": makam
          }
    return render(request, "makam/makam.html", ret)

def usul(request, usulid):
    usul = get_object_or_404(models.Usul, pk=usulid)

    ret = {"usul": usul
          }
    return render(request, "makam/usul.html", ret)

def form(request, formid):
    form = get_object_or_404(models.Form, pk=formid)

    ret = {"form": form
          }
    return render(request, "makam/form.html", ret)

def instrument(request, instrumentid):
    instrument = get_object_or_404(models.Instrument, pk=instrumentid)

    ret = {"instrument": instrument
          }
    return render(request, "makam/instrument.html", ret)
