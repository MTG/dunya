import django.contrib.auth.views
from django.conf import settings
from django.conf.urls import include, url, static
from django.contrib import admin
from django.views.generic.base import TemplateView

import dunya.views
import makam

urlpatterns = [
    url(r'^$', dunya.views.main, name="main"),
    url(r'^developers/$', dunya.views.developers, name="developers"),
    url(r'^about/terms', dunya.views.terms, name="terms"),
    url(r'^about/cookies', dunya.views.cookies, name="cookies"),
    url(r'^about/info',
        TemplateView.as_view(template_name="carnatic/general_info.html"),
        name="general-info"),
    url(r'^about/contact', dunya.views.contact, name="contact"),
    url(r'^api/carnatic/', include('carnatic.api_urls')),
    url(r'^api/hindustani/', include('hindustani.api_urls')),
    url(r'^api/makam/', include('makam.api_urls')),
    url(r'^api/andalusian/', include('andalusian.api_urls')),
    url(r'^carnatic/', include('carnatic.urls')),
    url(r'^motifdiscovery/', include('motifdiscovery.urls')),
    url(r'^hindustani/', include('hindustani.urls')),
    url(r'^andalusian/', include('andalusian.urls')),
    url(r'^makam/', include('makam.urls')),
    url(r'^jingju/', include('jingju.urls')),
    url(r'^document/', include('docserver.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^social/', include('account.urls')),
    url(r'^dashboard/', include('dashboard.urls')),
    url(r'^new/', include('frontend.urls')),
    url(r'^accounts/login/$', django.contrib.auth.views.login),
    url(r'^accounts/logout/$', django.contrib.auth.views.logout),
    url(r'^makamplayer/$', makam.views.makamplayer),
    url('', include('social_django.urls', namespace='social'))
]

if settings.DEBUG:
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
