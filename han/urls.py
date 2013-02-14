from django.conf.urls import patterns, url

from han import views

urlpatterns = patterns('',
    url(r'^$', views.main),
)

