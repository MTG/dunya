from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

import jingju.api

urlpatterns = [
    path("work", jingju.api.WorkList.as_view(), name="api-jingju-work-list"),
    path("work/<uuid:uuid>", jingju.api.WorkDetail.as_view(), name="api-jingju-work-detail"),
    path("recording", jingju.api.RecordingList.as_view(), name="api-jingju-recording-list"),
    path("recording/<uuid:uuid>", jingju.api.RecordingDetail.as_view(), name="api-jingju-recording-detail"),
    path("artist", jingju.api.ArtistList.as_view(), name="api-jingju-artist-list"),
    path("artist/<uuid:uuid>", jingju.api.ArtistDetail.as_view(), name="api-jingju-artist-detail"),
    path("release", jingju.api.ReleaseList.as_view(), name="api-jingju-release-list"),
    path("release/<uuid:uuid>", jingju.api.ReleaseDetail.as_view(), name="api-jingju-release-detail"),
    path("roletype", jingju.api.RoleTypeList.as_view(), name="api-jingju-roletype-list"),
    path("roletype/<uuid:uuid>", jingju.api.RoleTypeDetail.as_view(), name="api-jingju-roletype-detail"),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=["json", "api"])
