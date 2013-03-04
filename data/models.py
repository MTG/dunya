from django.db import models
from django_extensions.db.fields import UUIDField
from django.core.urlresolvers import reverse

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
    mbid = UUIDField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    startdate = models.DateField(blank=True, null=True)
    enddate = models.DateField(blank=True, null=True)
    artist_type = models.CharField(max_length=1, choices=TYPE_CHOICES, default='P')
    main_instrument = models.ForeignKey('Instrument', blank=True, null=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('carnatic-artist', args=[str(self.id)])

    def concerts(self):
        return ""

class Concert(models.Model):
    mbid = UUIDField(blank=True, null=True)
    location = models.ForeignKey('Location', blank=True, null=True)
    title = models.CharField(max_length=100)
    artists = models.ManyToManyField(Artist)
    tracks = models.ManyToManyField('Recording', related_name='concert')

    def __unicode__(self):
        ret = ", ".join([unicode(a) for a in self.artists.all()])
        if self.location:
            ret += " at " + unicode(self.location)
        return ret

    def get_absolute_url(self):
        return reverse('carnatic-concert', args=[str(self.id)])

class Work(models.Model):
    title = models.CharField(max_length=100)
    mbid = UUIDField(blank=True, null=True)
    composer = models.ForeignKey('Composer', blank=True, null=True)
    raaga = models.ForeignKey('Raaga', blank=True, null=True)
    taala = models.ForeignKey('Taala', blank=True, null=True)
    form = models.ForeignKey('Form', blank=True, null=True)

    def get_absolute_url(self):
        return reverse('carnatic-work', args=[str(self.id)])

class RecordingForms(models.Model):
    recording = models.ForeignKey('Recording')
    form = models.ForeignKey('Form')
    position = models.IntegerField()

    def get_absolute_url(self):
        return reverse('carnatic-recording', args=[str(self.id)])

class Form(models.Model):
    name = models.CharField(max_length=20)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('carnatic-form', args=[str(self.id)])

class Raaga(models.Model):
    name = models.CharField(max_length=20)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('carnatic-raaga', args=[str(self.id)])

class Taala(models.Model):
    name = models.CharField(max_length=20)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('carnatic-taala', args=[str(self.id)])

class WorkAttribute(models.Model):
    work = models.ForeignKey('Work')
    attribute_type = models.ForeignKey('WorkAttributeType')
    attribute_value_free = models.CharField(max_length=100, blank=True, null=True)
    attribute_value = models.ForeignKey('WorkAttributeTypeValue', blank=True, null=True)

class WorkAttributeType(models.Model):
    type_name = models.CharField(max_length=100)

class WorkAttributeTypeValue(models.Model):
    attribute_type = models.ForeignKey(WorkAttributeType)
    value = models.CharField(max_length=100)

class Recording(models.Model):
    title = models.CharField(max_length=100)
    work = models.ForeignKey(Work, blank=True, null=True)
    mbid = UUIDField(blank=True, null=True)
    length = models.IntegerField(blank=True, null=True)
    #raaga = models.ForeignKey(Raaga)
    #taala = models.ForeignKey(Taala)
    #forms = models.ManyToManyField(Form)

    def __unicode__(self):
        return title

    def get_absolute_url(self):
        return reverse('carnatic-recording', args=[str(self.id)])

class Instrument(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return name

    def get_absolute_url(self):
        return reverse('carnatic-instrument', args=[str(self.id)])

class InstrumentPerformance(models.Model):
    recording = models.ForeignKey(Recording)
    instrument = models.ForeignKey(Instrument)
    performer = models.ForeignKey(Artist)
    lead = models.BooleanField(default=False)

class Composer(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female')
    )
    name = models.CharField(max_length=200)
    mbid = UUIDField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    startdate = models.DateField(blank=True, null=True)
    enddate = models.DateField(blank=True, null=True)

    def __unicode__(self):
        return name

    def get_absolute_url(self):
        return reverse('carnatic-composer', args=[str(self.id)])

class Location(models.Model):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    lat = models.CharField(max_length=10, blank=True, null=True)
    lng = models.CharField(max_length=10, blank=True, null=True)

    def __unicode__(self):
        return self.name

