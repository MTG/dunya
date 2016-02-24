from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect

from andalusian import models

def main(request):
    return render(request, "andalusian/index.html")

def recording(request, uuid, title=None):
    recording = get_object_or_404(models.Recording, mbid=uuid)
    
    ret={
         "recording": recording,
        }
    return render(request, "andalusian/recording.html", ret)
