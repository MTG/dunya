from django.conf.urls import patterns, url

from hindustani import views

urlpatterns = patterns('',
    url(r'^$', views.main),
)
