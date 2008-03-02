from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to, direct_to_template
from profile.views import *
from settings import APIKEY

urlpatterns = patterns('',
    # Private profile
    (r'^$', private, {'APIKEY': APIKEY, 'template': 'profile/private.html'}),
    (r'^save/$', save),
    (r'^delete/$', delete, {'template': 'profile/delete.html'}),
    (r'^delete/done/$', direct_to_template, {'template': 'profile/delete_done.html'}),
    (r'^avatar/delete/$', avatarDelete),
    (r'^avatar/delete/(?P<avatar_id>[0-9]+)/$', avatarDelete),
    (r'^avatar/choose/$', avatarChoose, {'template': 'profile/avatar_choose.html'}),
    (r'^avatar/crop/(?P<avatar_id>[0-9]+)/$', avatarCrop, {'template': 'profile/avatar_crop.html'}),
    (r'^getcountry_info/(?P<lat>[0-9\.\-]+)/(?P<lng>[0-9\.\-]+)/$', fetch_geodata),

    # Public profile
    (r'^users/(?P<profile_user>[^/]*)/$', public, {'APIKEY': APIKEY, 'template': 'profile/public.html'}),

    # Vcard
    #(r'^users/(?P<user>[^/]*)/card/$', 'django.views.generic.list_detail.object_detail', dict(queryset=Foo.objects.all(), slug_field='slug', template_name="microformats/vcard.html",mimetype="text/x-vcard") ),
)
