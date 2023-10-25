from django.conf import settings
from django.urls import path, include
from django.contrib import admin
from django.views.generic.base import TemplateView

import makam.views

urlpatterns = [
    path('', TemplateView.as_view(template_name='dunya/index_dunya.html'), name='main'),
    path('developers/', TemplateView.as_view(template_name='dunya/developers.html'), name='developers'),
    path('about/terms', TemplateView.as_view(template_name='dunya/terms.html'), name='terms'),
    path('about/cookies', TemplateView.as_view(template_name='dunya/cookies.html'), name='cookies'),
    path('about/info', TemplateView.as_view(template_name='dunya/general_info.html'), name='general-info'),

    path('api/carnatic/', include('carnatic.api_urls')),
    path('api/hindustani/', include('hindustani.api_urls')),
    path('api/makam/', include('makam.api_urls')),
    path('api/andalusian/', include('andalusian.api_urls')),
    path('api/jingju/', include('jingju.api_urls')),

    path('carnatic/', include('carnatic.urls')),
    path('motifdiscovery/', include('motifdiscovery.urls')),
    path('hindustani/', include('hindustani.urls')),
    path('andalusian/', include('andalusian.urls')),
    path('makam/', include('makam.urls')),
    path('jingju/', include('jingju.urls')),

    path('document/', include('docserver.urls')),
    path('admin/', admin.site.urls),
    path('user/', include('account.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('makamplayer/', makam.views.makamplayer)
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
