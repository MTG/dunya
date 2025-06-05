from django.urls import path

from motifdiscovery import views

urlpatterns = [
    path("", views.main, name="motif-main"),
    path("artists", views.artists, name="motif-artists"),
    path("artist/<uuid:uuid>", views.artist, name="motif-artist"),
    path("release/<uuid:uuid>", views.release, name="motif-release"),
    path("seeds/<uuid:uuid>", views.seeds, name="motif-seeds"),
    path("recording/<uuid:uuid>", views.recinformation, name="motif-recinfo"),
    path("results/<uuid:uuid>/<int:seedid>", views.results, name="motif-results"),
    path("segment/<int:segmentid>.mp3", views.servesegment, name="motif-segment"),
]
