from django.conf.urls import patterns, url

from carnatic import views

urlpatterns = patterns('',
    url(r'^$', views.main),
)
