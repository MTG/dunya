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

from hindustani import models

def main(request):
    return render(request, "hindustani/index.html", {})

def composer(request, uuid):
    composer = get_object_or_404(models.Composer, mbid=uuid)

    ret = {"composer": composer
          }
    return render(request, "hindustani/composer.html", ret)

def artist(request, uuid):
    artist = get_object_or_404(models.Artist, mbid=uuid)

    ret = {"artist": artist
          }
    return render(request, "hindustani/artist.html", ret)

def release(request, uuid):
    release = get_object_or_404(models.Release, mbid=uuid)

    ret = {"release": release
          }
    return render(request, "hindustani/release.html", ret)

def recording(request, uuid):
    recording = get_object_or_404(models.Recording, mbid=uuid)

    ret = {"recording": recording
          }
    return render(request, "hindustani/recording.html", ret)

def work(request, uuid):
    work = get_object_or_404(models.Work, mbid=uuid)

    ret = {"work": work
          }
    return render(request, "hindustani/work.html", ret)

def laay(request, laayid):
    laay = get_object_or_404(models.Laay, pk=laayid)

    ret = {"laay": laay
          }
    return render(request, "hindustani/laay.html", ret)

def raag(request, raagid):
    raag = get_object_or_404(models.Raag, pk=raagid)

    ret = {"raag": raag
          }
    return render(request, "hindustani/raag.html", ret)

def taal(request, taalid):
    taal = get_object_or_404(models.Taal, pk=taalid)

    ret = {"taal": taal
          }
    return render(request, "hindustani/taal.html", ret)

def form(request, formid):
    form = get_object_or_404(models.Form, pk=formid)

    ret = {"form": form
          }
    return render(request, "hindustani/form.html", ret)

def instrument(request, instrumentid):
    instrument = get_object_or_404(models.Instrument, pk=instrumentid)

    ret = {"instrument": instrument
          }
    return render(request, "hindustani/instrument.html", ret)

