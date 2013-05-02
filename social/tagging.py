from django.db.models import Count
from carnatic.models import *
from social.models import *

def tag_cloud(artistid):
    MAX_WEIGHT = 5
    #artist_tags = Tag.objects.filter(artist_id="1").values('tag','artist').annotate(freq_tag=Count('tag'))
    artist_tags = ArtistTag.objects.filter(artist_id=artistid).values('tag','artist').annotate(freq_tag=Count('tag'))
    #tags = Tag.objects.order_by('name')
    
    if len(artist_tags)>0:
        # Calculate artist_tag, min and max counts.
        min_count = max_count = artist_tags[0]['freq_tag']
        
        for artist_tag in artist_tags:
            artist_tag['tag_name'] = Tag.objects.get(pk=artist_tag['tag']).name
            artist_tag_count = artist_tag['freq_tag']
            if artist_tag_count < min_count:
                min_count = artist_tag_count
            if max_count < artist_tag_count:
                max_count = artist_tag_count
                
        # Calculate count range. Avoid dividing by zero.
        rango = float(max_count - min_count)
        if rango == 0.0:
            rango = 1.0
            
        # Calculate artist_tag weights.
        for artist_tag in artist_tags:
            artist_tag['freq_tag'] = int(
                MAX_WEIGHT * (artist_tag['freq_tag'] - min_count) / rango)
    return artist_tags
