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

from hindustani import models
from django.contrib import admin

class WorkRaagaInline(admin.TabularInline):
    model = models.WorkRaaga
    extra = 1

class WorkTaalaInline(admin.TabularInline):
    model = models.WorkTaala
    extra = 1

class ReleaseRecordingInline(admin.TabularInline):
    model = models.ReleaseRecording
    extra = 1

class WorkAdmin(admin.ModelAdmin):
    inlines = (WorkRaagaInline, WorkTaalaInline)

class ReleaseAdmin(admin.ModelAdmin):
    inlines = (ReleaseRecordingInline, )

admin.site.register(models.GeographicRegion)
admin.site.register(models.Artist)
admin.site.register(models.ArtistAlias)
admin.site.register(models.Release, ReleaseAdmin)
admin.site.register(models.Raaga)
admin.site.register(models.Taala)
admin.site.register(models.Work, WorkAdmin)
admin.site.register(models.Recording)
admin.site.register(models.Instrument)
admin.site.register(models.InstrumentPerformance)
admin.site.register(models.Composer)
admin.site.register(models.ComposerAlias)



