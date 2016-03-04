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
 
    try:
        score = docserver.util.docserver_get_url(uuid, "svgscore", "score", 1, version=0.1)
    except docserver.util.NoFileException:
        score = None
     
    try:
        smallimage = docserver.util.docserver_get_url(uuid, "smallaudioimages", "smallfull", 1, version=0.1)
    except docserver.util.NoFileException:
        smallimage = None
       
   
    ret={
         "recording": recording,
         "audio": audio,
         "scoreurl": score,
         "smallimageurl": smallimage,
        }
    return render(request, "andalusian/recording.html", ret)
