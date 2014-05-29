import re
from django.conf import settings
from carnatic.models import *
from carnatic.urls import uuid_match

def navigation_header(request):
    displayhist = [] 
    for entity in request.session.get('navigation_history', []):
        item_type = entity[0]
        id_ = entity[1]
        if item_type == 'artist':
            item = Artist.objects.get(mbid=id_) 
        elif item_type == 'concert':
            item = Concert.objects.get(mbid=id_)
        elif item_type == 'instrument':
            item = Instrument.objects.get(id=id_)
        elif item_type == 'raaga':
            item = Raaga.objects.get(id=id_)
        elif item_type == 'taala':
            item = Taala.objects.get(id=id_)
        else:
            continue 
        displayhist.append((item_type, item)) 

    return {"navigation_history": displayhist}
