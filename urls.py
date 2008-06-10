from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from userprofile.views import *
from django.conf import settings

urlpatterns = patterns('',
    # Private profile
    (r'^manage/$', overview, { 'section': 'overview', 'APIKEY': settings.APIKEY, 'template': 'userprofile/overview.html'}),
    (r'^edit/(?P<section>location)/$', profile, {'APIKEY': settings.APIKEY, 'template': 'userprofile/location.html'}),
    (r'^edit/(?P<section>personal)/$', profile, {'template': 'userprofile/personal.html'}),
    (r'^edit/(?P<section>personal|location)/done/$', direct_to_template, {'template': 'userprofile/profile_done.html'}),
    (r'^delete/$', delete, { 'section': 'delete', 'template': 'userprofile/delete.html'}),
    (r'^delete/done/$', direct_to_template, { 'section': 'delete', 'template': 'userprofile/delete_done.html'}),
    (r'^public/$', makepublic, { 'section': 'makepublic', 'APIKEY': settings.APIKEY, 'template': 'userprofile/makepublic.html'}),
    (r'^edit/avatar/$', avatarchoose, { 'section': 'avatar', 'websearch': settings.WEBSEARCH, 'template': 'userprofile/avatar_choose.html'}),
    (r'^edit/avatar/delete/$', avatardelete),
    (r'^edit/avatar/search/$', searchimages, { 'section': 'avatar', 'template': 'userprofile/avatar_search.html'}),
    (r'^edit/avatar/crop/$', avatarcrop, { 'section': 'avatar', 'template': 'userprofile/avatar_crop.html'}),
    (r'^edit/avatar/crop/done/$', direct_to_template, { 'section': 'avatar', 'template': 'userprofile/avatar_done.html'}),
    (r'^getcountry_info/(?P<lat>[0-9\.\-]+)/(?P<lng>[0-9\.\-]+)/$', fetch_geodata),

    # Public profile
    (r'^users/(?P<current_user>[a-zA-Z0-9\-_]*)/$', public, {'APIKEY': settings.APIKEY, 'template': 'userprofile/public.html'}),

)
