from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from userprofile.views import *
from django.conf import settings

urlpatterns = patterns('',
    # Private profile
    (r'^$', private, {'APIKEY': settings.APIKEY, 'template': 'userprofile/private.html'}),
    (r'^edit/location/$', private, {'APIKEY': settings.APIKEY, 'template': 'userprofile/location.html'}),
    (r'^edit/personal/$', private, {'template': 'userprofile/personal.html'}),
    (r'^save/$', save),
    (r'^delete/$', delete, {'template': 'userprofile/delete.html'}),
    (r'^delete/done/$', direct_to_template, {'template': 'userprofile/delete_done.html'}),
    (r'^avatar/delete/$', avatarDelete),
    (r'^avatartemp/delete/$', avatarDelete, { 'temp': True }),
    (r'^avatar/choose/$', avatarChoose, {'websearch': settings.WEBSEARCH, 'template': 'userprofile/avatar_choose.html'}),
    (r'^avatar/searchimages/$', searchimages, {'template': 'userprofile/searchimages.html'}),
    (r'^avatar/crop/$', avatarCrop, {'template': 'userprofile/avatar_crop.html'}),
    (r'^getcountry_info/(?P<lat>[0-9\.\-]+)/(?P<lng>[0-9\.\-]+)/$', fetch_geodata),

    # Public profile
    (r'^users/(?P<current_user>[a-zA-Z0-9\-_]*)/$', public, {'APIKEY': settings.APIKEY, 'template': 'userprofile/public.html'}),

)
