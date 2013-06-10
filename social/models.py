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
    user = models.ForeignKey(User, unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    birthday = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='gallery', blank=True)
    def __unicode__(self):
        return unicode(self.user)

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
    name = models.CharField(max_length=128, unique=True)
    
    def __unicode__(self):
        return self.name

class Annotation(models.Model):
    user = models.ForeignKey(User)
    tag = models.ForeignKey(Tag)
    entity_id = models.IntegerField()
    entity_type = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True)
    class Meta:
        unique_together = (("user", "tag", "entity_id", "entity_type"),)
    def __unicode__(self):
        return u"('%s','%s','%s')" % (self.entity_type, self.tag , self.user)
    
class UserFollowsUser(models.Model):
    user_follower = models.ForeignKey(User, related_name='follow_set')
    user_followed = models.ForeignKey(User, related_name='to_follow_set')
    timestamp = models.DateTimeField('date follow')
    class Meta:
        unique_together = (("user_follower", "user_followed"),)
    def __unicode__(self):
        return u"('%s','%s','%s')" % (self.user_follower.username, self.user_followed.username, self.timestamp)   

