from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to, direct_to_template
from profile.views import *
from settings import APIKEY

urlpatterns = patterns('',
    # Private profile
    (r'^$', private, {'APIKEY': APIKEY, 'template': 'profile/private.html'}),
    (r'^save/$', save),
    (r'^delete/$', delete, {'template': 'profile/delete_confirm.html'}),
    (r'^delete/done/$', direct_to_template, {'template': 'profile/delete_success.html'}),
    (r'^avatar/delete/$', avatarDelete),
    (r'^avatar/delete/(?P<avatar_id>[0-9]+)/$', avatarDelete),
    (r'^avatar/(?P<step>one|two)/$', avatar, {'template': 'profile/avatar.html'}),
    (r'^getcountry_info/(?P<lat>[0-9\.\-]+)/(?P<lng>[0-9\.\-]+)/$', fetch_geodata),

    # Public profile
    (r'^users/(?P<user>[^/]*)/$', public, {'template': 'profile/public.html'}),

    # Vcard
    #(r'^users/(?P<user>[^/]*)/card/$', 'django.views.generic.list_detail.object_detail', dict(queryset=Foo.objects.all(), slug_field='slug', template_name="microformats/vcard.html",mimetype="text/x-vcard") ),
)
