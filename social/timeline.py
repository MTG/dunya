from django.contrib.comments import Comment
from carnatic.models import *
from social.models import *
from datetime import *


def timeline(users_id):
    comment_list = []
    
    #date = datetime.date.today()
    #start_week = date - datetime.timedelta(date.weekday())
    #end_week = start_week + datetime.timedelta(7)
    #entries = Entry.objects.filter(created_at__range=[start_week, end_week])
    date = datetime.now()
    end_period = date
    start_period = date - timedelta(days=15)
    
    #Primero se filtra por usuario y del resultado se filtra por rango de fechas
    comments = Comment.objects.filter(user_id__in=users_id).filter(submit_date__range=[start_period, end_period]).order_by("-submit_date")
    #comments = Comment.objects.filter(user_id__in=users_id).order_by("-submit_date")
    
    for comment in comments:
        #if comment.submit_date < datetime.now()-timedelta(days=10):
        #   break
        micomment = {"type": "comment",
                    "value": comment.comment,
                    "content_type": comment.content_type.model,
                    "content_id": comment.object_pk,
                    "user_id": comment.user_id,
                    "submit_date": comment.submit_date}
        micomment["username"] = User.objects.get(pk=micomment["user_id"]).username        
        if micomment['content_type'] == "artist":
            micomment["content_name"] = Artist.objects.get(pk=micomment['content_id']).name
        elif micomment['content_type'] == "concert":
            micomment["content_name"] = Concert.objects.get(pk=micomment['content_id']).title
        elif micomment['content_type'] == "work":
            micomment["content_name"] = Work.objects.get(pk=micomment['content_id']).title
        elif micomment['content_type'] == "recording":
            micomment["content_name"] = Recording.objects.get(pk=micomment['content_id']).title
            
        comment_list.append(micomment)
    
    
    tag_list=[]
    
    artisttags = ArtistTag.objects.filter(user_id__in=users_id).filter(timestamp__range=[start_period, end_period]).order_by("-timestamp")
    concerttags = ConcertTag.objects.filter(user_id__in=users_id).filter(timestamp__range=[start_period, end_period]).order_by("-timestamp")
    worktags = WorkTag.objects.filter(user_id__in=users_id).filter(timestamp__range=[start_period, end_period]).order_by("-timestamp")
    recordingtags = RecordingTag.objects.filter(user_id__in=users_id).filter(timestamp__range=[start_period, end_period]).order_by("-timestamp")

    for artisttag in artisttags:
        mitag = {"type": "tag",
                    "tag_id": artisttag.tag_id,
                    "content_type": "artist",
                    "content_id": artisttag.artist_id,
                    "user_id": artisttag.user_id,
                    "submit_date": artisttag.timestamp}
        mitag["username"] = User.objects.get(pk=mitag["user_id"]).username        
        mitag["value"] = Tag.objects.get(pk=mitag['tag_id']).name
        mitag["content_name"] = Artist.objects.get(pk=mitag['content_id']).name
            
        tag_list.append(mitag)
    
    for concerttag in concerttags:
        mitag = {"type": "tag",
                    "tag_id": concerttag.tag_id,
                    "content_type": "concert",
                    "content_id": concerttag.concert_id,
                    "user_id": concerttag.user_id,
                    "submit_date": concerttag.timestamp}
        mitag["username"] = User.objects.get(pk=mitag["user_id"]).username        
        mitag["value"] = Tag.objects.get(pk=mitag['tag_id']).name
        mitag["content_name"] = Concert.objects.get(pk=mitag['content_id']).title
            
        tag_list.append(mitag)

    for worktag in worktags:
        mitag = {"type": "tag",
                    "tag_id": worktag.tag_id,
                    "content_type": "work",
                    "content_id": worktag.work_id,
                    "user_id": worktag.user_id,
                    "submit_date": worktag.timestamp}
        mitag["username"] = User.objects.get(pk=mitag["user_id"]).username        
        mitag["value"] = Tag.objects.get(pk=mitag['tag_id']).name
        mitag["content_name"] = Work.objects.get(pk=mitag['content_id']).title
            
        tag_list.append(mitag)
    
    for recordingtag in recordingtags:
        mitag = {"type": "tag",
                    "tag_id": recordingtag.tag_id,
                    "content_type": "recording",
                    "content_id": recordingtag.recording_id,
                    "user_id": recordingtag.user_id,
                    "submit_date": recordingtag.timestamp}
        mitag["username"] = User.objects.get(pk=mitag["user_id"]).username        
        mitag["value"] = Tag.objects.get(pk=mitag['tag_id']).name
        mitag["content_name"] = Recording.objects.get(pk=mitag['content_id']).title
            
        tag_list.append(mitag)    
        
    final_list = comment_list + tag_list
    
    
    
    return sorted(final_list, key=lambda x: x['submit_date'], reverse=True)



