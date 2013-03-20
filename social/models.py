from django.contrib.auth.models import User
from django_extensions.db.fields import UUIDField
from django.db import models
from django.db.models.base import Model

# Create your models here.
class Instrument(models.Model):
    name = models.CharField(max_length=200)

class Artist(models.Model):
    GENDER_CHOICES = (
       ('M', 'Male'),
       ('F', 'Female')
   )
    TYPE_CHOICES = (
       ('P', 'Person'),
       ('G', 'Group')
   )
    name = models.CharField(max_length=200)
    uuid = UUIDField(primary_key=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    startdate = models.DateField()
    enddate = models.DateField()
    artist_type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    main_instrument = models.ForeignKey('Instrument')

class Raaga(models.Model):
    name = models.CharField(max_length=20)

class Taala(models.Model):
    name = models.CharField(max_length=20)

class Work(models.Model):
    mbid = UUIDField(primary_key=True)
    raaga = models.ForeignKey(Raaga)
    taala = models.ForeignKey(Taala)

class Concert(models.Model):
    STATUS_CHOICES = (
       ('O', 'Official'),
       ('P', 'Promotional'),
       ('B', 'Bootleg'),
       ('S', 'Pseudo-Release')
   )
    QUALITY_CHOICES = (
       ('N', 'Normal'),
              
   )
    mbid = UUIDField(primary_key=True)
    title = models.CharField(max_length=255)
    date = models.DateField('date performed')
    country = models.CharField(max_length=2)
    city = models.CharField(max_length=100, default='unknown')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    quality = models.CharField(max_length=1, choices=QUALITY_CHOICES)
        
class Recording(models.Model):
    work = models.ForeignKey(Work)
    mbid = UUIDField(primary_key=True)
    title = models.CharField(max_length=255)
    length = models.IntegerField()
    concert = models.ForeignKey(Concert)
    raaga = models.ForeignKey(Raaga)
    taala = models.ForeignKey(Taala)

class InstrumentPerformance(models.Model):
    recording = models.ForeignKey(Recording)
    instrument = models.ForeignKey(Instrument)
    performer = models.ForeignKey(Artist)


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

class Comment(models.Model):
    comment = models.TextField()

class Tag(models.Model):
    tag = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    
class ArtistTag(models.Model):
    user = models.ForeignKey(User)
    tag = models.ForeignKey(Tag)
    artist = models.ForeignKey(Artist)
    timestamp = models.DateTimeField('date tagged')
    class Meta:
        unique_together = (("user", "tag", "artist"),)

class ArtistComment(models.Model):
    user = models.ForeignKey(User)
    comment = models.ForeignKey(Comment)
    artist = models.ForeignKey(Artist)
    timestamp = models.DateTimeField('date commented')
    class Meta:
        unique_together = (("user", "comment", "artist"),)
    
