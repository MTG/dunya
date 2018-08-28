from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

import jingju.api

uuid_match = r'(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'

urlpatterns = [

    # url(r'^instrument$', carnatic.api.InstrumentList.as_view(), name='api-carnatic-instrument-list'),
    # url(r'^instrument/(?P<pk>\d+)$', carnatic.api.InstrumentDetail.as_view(), name='api-carnatic-instrument-detail'),

    url(r'^work$', jingju.api.WorkList.as_view(), name='api-jingju-work-list'),
    # url(r'^work/%s$' % uuid_match, carnatic.api.WorkDetail.as_view(), name='api-carnatic-work-detail'),

    url(r'^recording$', jingju.api.RecordingList.as_view(), name='api-jingju-recording-list'),
    # url(r'^recording/%s$' % uuid_match, carnatic.api.RecordingDetail.as_view(), name='api-carnatic-recording-detail'),

    # url(r'^artist$', carnatic.api.ArtistList.as_view(), name='api-carnatic-artist-list'),
    # url(r'^artist/%s$' % uuid_match, carnatic.api.ArtistDetail.as_view(), name='api-carnatic-artist-detail'),

    # url(r'^concert$', carnatic.api.ConcertList.as_view(), name='api-carnatic-concert-list'),
    # url(r'^concert/%s$' % uuid_match, carnatic.api.ConcertDetail.as_view(), name='api-carnatic-concert-detail')
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])