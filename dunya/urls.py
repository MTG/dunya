from django.conf.urls import patterns, include, url, static

from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^/?', include('browse.urls')),
    url(r'^carnatic/', include('carnatic.urls')),
    url(r'^hindustani', include('hindustani.urls')),
    url(r'^makam', include('makam.urls')),
    url(r'^han', include('han.urls')),
    url(r'^document/', include('docserver.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^social/', include('social.urls')),
    url(r'^dashboard/', include('dashboard.urls')),
)

#if settings.DEBUG:
#    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
