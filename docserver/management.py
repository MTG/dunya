from django.db.models.signals import post_syncdb

from docserver import models
from docserver import filetypes

import inspect

"""A post-syncdb hook to create DocumentConversion objects
"""
def create_docconverters(sender, **kwargs):
    for cl in inspect.getmembers(sender):
        if filetypes.FileType in cl.__bases__:
            inst = cl()

#post_syncdb.connect(create_docconverters)
