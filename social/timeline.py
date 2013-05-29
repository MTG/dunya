from django.contrib.comments import Comment
from carnatic.models import *
from social.models import *
from datetime import *


def get_comments(users_id, start_period, end_period):
    comment_list = []
    #We first filter by user and then by timestamp
    comments = Comment.objects.filter(user_id__in=users_id).filter(submit_date__range=[start_period, end_period]).order_by("-submit_date")
    
    #comments = Comment.objects.filter(user_id__in=users_id).order_by("-submit_date")
    
    for comment in comments:
        #if comment.submit_date < datetime.now()-timedelta(days=10):
        #   break
        micomment = {"type": "comment",
                     "id": comment.id,
                    "value": comment.comment,
                    "content_type": comment.content_type.model,
                    "content_id": comment.object_pk,
                    "user_id": comment.user_id,
                    "submit_date": comment.submit_date}
        print "MODEL-->", comment.content_type
        micomment["username"] = User.objects.get(pk=micomment["user_id"]).username
        print micomment["username"] 
        if micomment['content_type'] == "artist":
            print "aqui"
            micomment["content_name"] = Artist.objects.get(pk=micomment['content_id']).name
            print micomment["content_name"]
        elif micomment['content_type'] == "concert":
            micomment["content_name"] = Concert.objects.get(pk=micomment['content_id']).title
        elif micomment['content_type'] == "work":
            micomment["content_name"] = Work.objects.get(pk=micomment['content_id']).title
        elif micomment['content_type'] == "recording":
            micomment["content_name"] = Recording.objects.get(pk=micomment['content_id']).title
            
        comment_list.append(micomment)
    return comment_list

def get_artist_tags(users_id, start_period, end_period):
    artisttags = ArtistTag.objects.filter(user_id__in=users_id).filter(timestamp__range=[start_period, end_period]).order_by("-timestamp")
    tag_list = []
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
    return tag_list

def get_concert_tags(users_id, start_period, end_period):
    tag_list = []
    concerttags = ConcertTag.objects.filter(user_id__in=users_id).filter(timestamp__range=[start_period, end_period]).order_by("-timestamp")
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
    return tag_list


def get_work_tags(users_id, start_period, end_period):
    tag_list = []
    worktags = WorkTag.objects.filter(user_id__in=users_id).filter(timestamp__range=[start_period, end_period]).order_by("-timestamp")
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
    return tag_list

def get_recording_tags(users_id, start_period, end_period):
    tag_list = []
    recordingtags = RecordingTag.objects.filter(user_id__in=users_id).filter(timestamp__range=[start_period, end_period]).order_by("-timestamp")
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
    return tag_list
    

def timeline(users_id):
    
    
    #date = datetime.date.today()
    #start_week = date - datetime.timedelta(date.weekday())
    #end_week = start_week + datetime.timedelta(7)
    #entries = Entry.objects.filter(created_at__range=[start_week, end_week])
    date = datetime.now()
    end_period = date
    start_period = date - timedelta(days=15)
    
    comment_list = get_comments(users_id, start_period, end_period)
    
    tag_list=[]
    tag_list += get_artist_tags(users_id, start_period, end_period)
    tag_list += get_concert_tags(users_id, start_period, end_period)
    tag_list += get_work_tags(users_id, start_period, end_period)
    tag_list += get_recording_tags(users_id, start_period, end_period)

    final_list = comment_list + tag_list
    
    return sorted(final_list, key=lambda x: x['submit_date'], reverse=True)



