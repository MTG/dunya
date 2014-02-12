from django.db import models
from django_extensions.db.fields import UUIDField

class Orchestra(models.Model):
	mbid = UUIDField(blank=True, null=True)
	name = models.CharField(max_length=255)
	alias = models.CharField(max_length=255)
	
class OrchestraAlias(models.Model):
	name = models.CharField(max_length=255)
	orchestra = models.ForeignKey("Orchestra", related_name="aliases")
	
	def __unicode__(self):
		return self.name

class Artist(models.Model):
	GENDER_CHOICES = (
		('M', 'Male'),
		('F', 'Female')
	)
	name = models.CharField(max_length=200)
	mbid = UUIDField(blank=True, null=True)
	gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
	begin = models.CharField(max_length=10, blank=True, null=True)
	end = models.CharField(max_length=10, blank=True, null=True)

class ArtistAlias(models.Model):
	name = models.CharField(max_length=200)
	artist = models.ForeignKey("Artist", related_name="aliases")
	
	def __unicode__(self):
		return self.name

class AlbumType(models.Model):
	type = models.CharField(max_length=255)
	
	def __unicode__(self):
		return self.type
	

class Album(models.Model):
	mbid = UUIDField(blank=True, null=True)
	title = models.CharField(max_length=255)
	album_type = models.ForeignKey(AlbumType, blank=True, null=True)
	
class AlbumAlias(models.Model):
	title = models.CharField(max_length=255)
	album = models.ForeignKey("Album", related_name="aliases")
	
	def __unicode__(self):
		return self.name
	
class Recording(models.Model):
	mbid = UUIDField(blank=True, null=True)
	title = models.CharField(max_length=255)
	album = models.ForeignKey('Album')
	length = models.IntegerField(blank=True, null=True)
	year = models.IntegerField(blank=True, null=True)
	genre = models.CharField(max_length=100)
	director = models.ForeignKey('Artist')
	
class RecordingAlias(models.Model):
	title = models.CharField(max_length=255)
	recording = models.ForeignKey("Recording", related_name="aliases")
	
	def __unicode__(self):
		return self.name
	
class RecordingOrchestra(models.Model):
	recording = models.ForeignKey('Recording')
	orchestra = models.ForeignKey('Orchestra')
	class Meta:
		unique_together = (("recording", "orchestra"),)

class Instrument(models.Model):
	percussion = models.BooleanField(default=False)
	name = models.CharField(max_length=50)
	
	def __unicode__(self):
		return self.name

class InstrumentAlias(models.Model):
	name = models.CharField(max_length=50)
	instrument = models.ForeignKey("Instrument", related_name="aliases")
	
	def __unicode__(self):
		return self.name

class InstrumentPerformance(models.Model):
    class Meta:
        abstract = True
    recording_orchestra = models.ForeignKey('RecordingOrchestra')
    performer = models.ForeignKey('Artist')
    instrument = models.ForeignKey('Instrument')
    lead = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s playing %s on %s" % (self.performer, self.instrument, self.recording)

class OrchestraPerformer(models.Model):
	orchestra = models.ForeignKey('Orchestra')
	performer = models.ForeignKey('Artist')
	instrument = models.ForeignKey('Instrument')
	director = models.BooleanField(default=False)
	begin = models.CharField(max_length=10, blank=True, null=True)
	end = models.CharField(max_length=10, blank=True, null=True)

class Tab(models.Model):
	name = models.CharField(max_length=50)
	def __unicode__(self):
		return self.name
	
class TabAlias(models.Model):
	name = models.CharField(max_length=50)
	tab = models.ForeignKey("Tab", related_name="aliases")
	
	def __unicode__(self):
		return self.name

class Nawba(models.Model):
	name = models.CharField(max_length=50)
	def __unicode__(self):
		return self.name
	
class NawbaAlias(models.Model):
	name = models.CharField(max_length=50)
	nawba = models.ForeignKey("Nawba", related_name="aliases")
	
	def __unicode__(self):
		return self.name
	
class Mizan(models.Model):
	name = models.CharField(max_length=50)
	def __unicode__(self):
		return self.name
	
class MizanAlias(models.Model):
	name = models.CharField(max_length=50)
	mizan = models.ForeignKey("Mizan", related_name="aliases")
	
	def __unicode__(self):
		return self.name
	
class FormType(models.Model):
	type = models.CharField(max_length=50)
	def __unicode__(self):
		return self.type
	
class Form(models.Model):
	name = models.CharField(max_length=50)
	form_type = models.ForeignKey(FormType, blank=True, null=True)
	def __unicode__(self):
		return self.name
	
class FormAlias(models.Model):
	name = models.CharField(max_length=50)
	form = models.ForeignKey("Form", related_name="aliases")
	
	def __unicode__(self):
		return self.name
	
class Section(models.Model):
	recording = models.ForeignKey('Recording')
	order_number = models.IntegerField(blank=True, null=True) #Maybe not necessary if start_time and end_time are known
	start_time = models.CharField(max_length=8, blank=True, null=True)
	end_time = models.CharField(max_length=8, blank=True, null=True)
	tab = models.ForeignKey('Tab', blank=True, null=True)
	nawba = models.ForeignKey('Nawba', blank=True, null=True)
	mizan = models.ForeignKey('Mizan', blank=True, null=True)
	form = models.ForeignKey('Form', blank=True, null=True)
	
class InstrumentSectionPerformance(models.Model):
	section = models.ForeignKey('Section')
	performer = models.ForeignKey('Artist')
	instrument = models.ForeignKey('Instrument')
	lead = models.BooleanField(default=False)
	def __unicode__(self):
		return "%s playing %s on section %s of recording %s" % (self.performer, self.instrument, self.section, self.section.recording)


class Sanaa(models.Model):
	title = models.CharField(max_length=255)
	def __unicode__(self):
		return self.title
	
class SanaaAlias(models.Model):
	title = models.CharField(max_length=255)
	sanaa = models.ForeignKey("Sanaa", related_name="aliases")
	def __unicode__(self):
		return self.name

class PoemType(models.Model):
	type = models.CharField(max_length=50)
	def __unicode__(self):
		return self.type

class Poem(models.Model):
	identifier = models.CharField(max_length=100, blank=True, null=True)
	first_words = models.CharField(max_length=255, blank=True, null=True)
	type = models.ForeignKey(PoemType, blank=True, null=True)
	text = models.TextField()
	def __unicode__(self):
		return self.identifier
	
class PoemAlias(models.Model):
	identifier = models.CharField(max_length=100, blank=True, null=True)
	poem = models.ForeignKey("Poem", related_name="aliases")
	def __unicode__(self):
		return self.identifier
	
class SectionSanaaPoem(models.Model):
	section = models.ForeignKey('Section')
	sanaa = models.ForeignKey('Sanaa')
	poem = models.ForeignKey('Poem')
	order_number = models.IntegerField(blank=True, null=True)
