from dashboard import models
from django.contrib import admin

admin.site.register(models.CompletenessChecker)
admin.site.register(models.CollectionState)
admin.site.register(models.Collection)
admin.site.register(models.CollectionLogMessage)
admin.site.register(models.MusicbrainzReleaseState)
admin.site.register(models.MusicbrainzRelease)
admin.site.register(models.MusicbrainzReleaseLogMessage)
admin.site.register(models.CollectionDirectory)
admin.site.register(models.CollectionDirectoryLogMessage)
admin.site.register(models.CollectionFileState)
admin.site.register(models.CollectionFile)
admin.site.register(models.CollectionFileLogMessage)
admin.site.register(models.CollectionFileResult)
admin.site.register(models.MusicbrainzReleaseResult)
