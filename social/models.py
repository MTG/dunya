from django.contrib.auth.models import User
from django_extensions.db.fields import UUIDField
from django.db import models
from django.db.models.base import Model
from carnatic.models import *


################ SOCIAL PART #########################

class UserProfile(models.Model):
    #The primary attributes of the default user are:
    #username
    #password
    #email
    #first name
    #last name
    
    #user = models.OneToOneField(User)
    user = models.ForeignKey(User, unique=True)
    birthday = models.DateField()
    avatar = models.ImageField(upload_to='gallery')
    

class Playlist(models.Model):
    #la PK id ya la genera django automaticamente
    id_user = models.ForeignKey(User)
    timestamp = models.DateTimeField('date created')
    name = models.CharField(max_length=100)
    public = models.BooleanField()
    recordings = models.ManyToManyField(Recording)

#class Comment(models.Model):
#    comment = models.TextField()

#class Tag(models.Model):
#    tag = models.CharField(max_length=100)
#    category = models.CharField(max_length=100)
#    
#class ArtistTag(models.Model):
#    user = models.ForeignKey(User)
#    tag = models.ForeignKey(Tag)
#    artist = models.ForeignKey(Artist)
#    timestamp = models.DateTimeField('date tagged')
#    class Meta:
#        unique_together = (("user", "tag", "artist"),)

#class ArtistComment(models.Model):
#    user = models.ForeignKey(User)
#    comment = models.ForeignKey(Comment)
#    artist = models.ForeignKey(Artist)
#    timestamp = models.DateTimeField('date commented')
#    class Meta:
#        unique_together = (("user", "comment", "artist"),)
