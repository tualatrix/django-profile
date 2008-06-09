from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from userprofile.views import *
from django.conf import settings

urlpatterns = patterns('',
    # Private profile
    (r'^$', overview, {'APIKEY': settings.APIKEY, 'template': 'userprofile/overview.html'}),
    (r'^edit/(?P<type>location)/$', private, {'APIKEY': settings.APIKEY, 'template': 'userprofile/location.html'}),
    (r'^edit/(?P<type>personal)/$', private, {'template': 'userprofile/personal.html'}),
    (r'^(?P<type>personal|location)/save/$', save),
    (r'^delete/$', delete, {'template': 'userprofile/delete.html'}),
    (r'^delete/done/$', direct_to_template, {'template': 'userprofile/delete_done.html'}),
    (r'^avatar/delete/$', avatarDelete),
    (r'^avatartemp/delete/$', avatarDelete, { 'temp': True }),
    (r'^edit/avatar/$', avatarChoose, {'websearch': settings.WEBSEARCH, 'template': 'userprofile/avatar.html'}),
    (r'^avatar/search/$', searchimages, {'template': 'userprofile/avatarsearch.html'}),
    (r'^avatar/crop/$', avatarCrop, {'template': 'userprofile/avatar_crop.html'}),
    (r'^getcountry_info/(?P<lat>[0-9\.\-]+)/(?P<lng>[0-9\.\-]+)/$', fetch_geodata),

    # Public profile
    (r'^users/(?P<current_user>[a-zA-Z0-9\-_]*)/$', public, {'APIKEY': settings.APIKEY, 'template': 'userprofile/public.html'}),

)
