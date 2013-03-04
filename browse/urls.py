from django.conf.urls import patterns, url

from browse import views

urlpatterns = patterns('',
    url(r'^$', views.main, name='home'),
)
