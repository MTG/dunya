from django.conf.urls import patterns, url

from dashboard import views

uuid_match = r'(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'

urlpatterns = patterns('',
    url(r'^$', views.index, name='dashboard-home'),
    #url(r'^(?P<cslug>[^/]+)$'),
    #url(r'^(?P<cslug>[^/]+)/%s$' % uuid_match),
)

