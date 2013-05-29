from django.db.models import Count
from carnatic.models import *
from social.models import *     
    

def tag_cloud(modelid, modeltype):
    MAX_WEIGHT = 5
    
    if modeltype == "artist":
        tags = ArtistTag.objects.filter(artist_id=modelid).values('tag','artist').annotate(freq_tag=Count('tag'))
        for tag in tags:
            tag['content_type'] = "artist"
    elif modeltype == "concert":
        tags = ConcertTag.objects.filter(concert_id=modelid).values('tag','concert').annotate(freq_tag=Count('tag'))
        for tag in tags:
            tag['content_type'] = "concert"
    elif modeltype == "recording":
        tags = RecordingTag.objects.filter(recording_id=modelid).values('tag','recording').annotate(freq_tag=Count('tag'))
        for tag in tags:
            tag['content_type'] = "recording"
    elif modeltype == "work":
        tags = WorkTag.objects.filter(work_id=modelid).values('tag','work').annotate(freq_tag=Count('tag'))
        for tag in tags:
            tag['content_type'] = "work"
    
    
    if len(tags)>0:
        # Calculate artist_tag, min and max counts.
        min_count = max_count = tags[0]['freq_tag']
        
        for tag in tags:
            tag['value'] = Tag.objects.get(pk=tag['tag']).name
            tag_count = tag['freq_tag']
            if tag_count < min_count:
                min_count = tag_count
            if max_count < tag_count:
                max_count = tag_count
                
        # Calculate count range. Avoid dividing by zero.
        rango = float(max_count - min_count)
        if rango == 0.0:
            rango = 1.0
            
        # Calculate artist_tag weights.
        for tag in tags:
            tag['freq_tag'] = int(
                MAX_WEIGHT * (tag['freq_tag'] - min_count) / rango)
    return tags

