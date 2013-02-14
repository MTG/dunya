from django.conf.urls import patterns, include, url, static

from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^document/', include('docserver.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

#if settings.DEBUG:
#    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
