from django.contrib.auth.models import User
from django_extensions.db.fields import UUIDField
from django.db import models
from django.db.models.base import Model
from carnatic.models import *
from django.db.models.signals import post_save


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
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    birthday = models.DateField(null=True)
    avatar = models.ImageField(upload_to='gallery', null=True)

def user_post_save(sender, instance, created, **kwargs):
    """Create a user profile when a new user account is created"""
    if created == True:
        p = UserProfile()
        p.user = instance
        p.save()

post_save.connect(user_post_save, sender=User)


class Playlist(models.Model):
    #la PK id ya la genera django automaticamente
    id_user = models.ForeignKey(User)
    timestamp = models.DateTimeField('date created')
    name = models.CharField(max_length=100)
    public = models.BooleanField()
    recordings = models.ManyToManyField(Recording)

class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True)
    artist = models.ManyToManyField(Artist)
    
    def __unicode__(self):
        return self.name


    


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


#class Comment(models.Model):
#    comment = models.TextField()

#class ArtistComment(models.Model):
#    user = models.ForeignKey(User)
#    comment = models.ForeignKey(Comment)
#    artist = models.ForeignKey(Artist)
#    timestamp = models.DateTimeField('date commented')
#    class Meta:
#        unique_together = (("user", "comment", "artist"),)
