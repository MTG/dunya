from docserver import models
from django.contrib import admin

admin.site.register(models.Collection)
admin.site.register(models.Document)
admin.site.register(models.FileType)
admin.site.register(models.File)
