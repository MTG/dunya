from django.conf.urls import patterns, include, url, static
from django.conf import settings
from django.contrib import admin
from django.contrib.comments.models import Comment
from django.views.generic.base import RedirectView

admin.autodiscover()

js_info_dict = {
    'packages': ('django.conf',),
}

urlpatterns = patterns('',
    # Examples:
    url(r'^$', RedirectView.as_view(pattern_name="carnatic-main"), name="main"),
    url(r'^/', RedirectView.as_view(pattern_name="carnatic-main")),
    url(r'^about/terms', 'dunya.views.terms', name="terms"),
    url(r'^about/cookies', 'dunya.views.cookies', name="cookies"),
    url(r'^about/contact', 'dunya.views.contact', name="contact"),
    url(r'^api/', include('dunya.api_urls')),
    url(r'^carnatic/', include('carnatic.urls')),
    url(r'^motifdiscovery/', include('motifdiscovery.urls')),
    url(r'^hindustani/', include('hindustani.urls')),
    url(r'^makam/', include('makam.urls')),
    url(r'^han/', include('han.urls')),
    url(r'^document/', include('docserver.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^social/', include('social.urls')),
    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^inplaceeditform/', include('inplaceeditform.urls')),
    url(r'^jsi18n$', 'django.views.i18n.javascript_catalog', js_info_dict),
    url(r'^dashboard/', include('dashboard.urls')),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
    url(r'^makamplayer/$', 'makam.views.makamplayer'),
)

if settings.DEBUG:
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
