from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from userprofile.views import *
from django.conf import settings

urlpatterns = patterns('',
    # Private profile
    (r'^$', private, {'APIKEY': settings.APIKEY, 'template': 'userprofile/private.html'}),
    (r'^save/$', save),
    (r'^delete/$', delete, {'template': 'userprofile/delete.html'}),
    (r'^delete/done/$', direct_to_template, {'template': 'userprofile/delete_done.html'}),
    (r'^avatar/delete/$', avatarDelete),
    (r'^avatar/delete/(?P<avatar_id>[0-9]+)/$', avatarDelete),
    (r'^avatar/choose/$', avatarChoose, {'template': 'userprofile/avatar_choose.html'}),
    (r'^avatar/crop/(?P<avatar_id>[0-9]+)/$', avatarCrop, {'template': 'userprofile/avatar_crop.html'}),
    (r'^getcountry_info/(?P<lat>[0-9\.\-]+)/(?P<lng>[0-9\.\-]+)/$', fetch_geodata),

    # Public profile
    (r'^users/(?P<user_slug>[a-zA-Z0-9\-_]*)/$', public, {'APIKEY': settings.APIKEY, 'template': 'userprofile/public.html'}),

)
