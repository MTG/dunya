# Copyright 2013,2014 Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of Dunya
#
# Dunya is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation (FSF), either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/

from carnatic import models
from django.contrib import admin

class WorkRaagaInline(admin.TabularInline):
    model = models.WorkRaaga
    extra = 1

class ArtistAliasInline(admin.TabularInline):
    model = models.ArtistAlias
    extra = 1

class WorkTaalaInline(admin.TabularInline):
    model = models.WorkTaala
    extra = 1

class ConcertRecordingInline(admin.TabularInline):
    model = models.ConcertRecording
    extra = 1

class InstrumentPerformanceInline(admin.TabularInline):
    model = models.InstrumentPerformance
    extra = 1

class WorkAdmin(admin.ModelAdmin):
    inlines = (WorkRaagaInline, WorkTaalaInline)
    exclude = ('images', )

class ConcertAdmin(admin.ModelAdmin):
    inlines = (ConcertRecordingInline, )
    exclude = ('images', )

class RaagaAdmin(admin.ModelAdmin):
    exclude = ('images', )

class TaalaAdmin(admin.ModelAdmin):
    exclude = ('images', )

class ArtistAdmin(admin.ModelAdmin):
    inlines = (ArtistAliasInline, )
    exclude = ('images', 'description')

class InstrumentAdmin(admin.ModelAdmin):
    exclude = ('images', 'description')

class RecordingAdmin(admin.ModelAdmin):
    inlines = (InstrumentPerformanceInline, )
    exclude = ('images', )

admin.site.register(models.GeographicRegion)
admin.site.register(models.Artist, ArtistAdmin)
admin.site.register(models.ArtistAlias)
admin.site.register(models.Concert, ConcertAdmin)
admin.site.register(models.Raaga, RaagaAdmin)
admin.site.register(models.Taala, TaalaAdmin)
admin.site.register(models.Work, WorkAdmin)
admin.site.register(models.Recording, RecordingAdmin)
admin.site.register(models.Instrument, InstrumentAdmin)
admin.site.register(models.Composer)
admin.site.register(models.Form)
admin.site.register(models.ComposerAlias)
