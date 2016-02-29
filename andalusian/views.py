from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect

from andalusian import models
import docserver

def main(request):
    return render(request, "andalusian/index.html")

def recording(request, uuid, title=None):
    recording = get_object_or_404(models.Recording, mbid=uuid)
 
    try:
        audio = docserver.util.docserver_get_mp3_url(uuid)
    except docserver.util.NoFileException:
        audio = None
    
   
    ret={
         "recording": recording,
         "audio": audio,
        }
    return render(request, "andalusian/recording.html", ret)
