from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

import jingju.api

uuid_match = r'(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'

urlpatterns = [
    url(r'^work$', jingju.api.WorkList.as_view(), name='api-jingju-work-list'),
    url(r'^work/%s$' % uuid_match, jingju.api.WorkDetail.as_view(), name='api-jingju-work-detail'),

    url(r'^recording$', jingju.api.RecordingList.as_view(), name='api-jingju-recording-list'),
    url(r'^recording/%s$' % uuid_match, jingju.api.RecordingDetail.as_view(), name='api-jingju-recording-detail'),

    url(r'^recording$', jingju.api.ReleaseList.as_view(), name='api-jingju-release-list'),
    url(r'^recording/%s$' % uuid_match, jingju.api.ReleaseDetail.as_view(), name='api-jingju-release-detail'),

    url(r'^artist$', jingju.api.ArtistList.as_view(), name='api-jingju-artist-list'),
    url(r'^artist/%s$' % uuid_match, jingju.api.ArtistDetail.as_view(), name='api-jingju-artist-detail'),

    url(r'^release$', jingju.api.ReleaseList.as_view(), name='api-jingju-release-list'),
    url(r'^release/%s$' % uuid_match, jingju.api.ReleaseDetail.as_view(), name='api-jingju-release-detail'),

    url(r'^roletype$', jingju.api.RoleTypeList.as_view(), name='api-jingju-roletype-list'),
    url(r'^roletype/%s$' % uuid_match, jingju.api.RoleTypeDetail.as_view(), name='api-jingju-roletype-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])
