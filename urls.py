from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib.auth import views
from userprofile.views import *
from django.conf import settings

APIKEY = hasattr(settings, "APIKEY") and settings.APIKEY or None
WEBSEARCH = hasattr(settings, "WEBSEARCH") and settings.WEBSEARCH or None

urlpatterns = patterns('',
    # Private profile
    (r'^profile/$', overview, { 'section': 'overview', 'APIKEY': APIKEY, 'template': 'userprofile/profile/overview.html'}),
    (r'^profile/edit/(?P<section>location)/$', profile, {'APIKEY': APIKEY, 'template': 'userprofile/profile/location.html'}),
    (r'^profile/edit/(?P<section>personal)/$', profile, {'template': 'userprofile/profile/personal.html'}),
    (r'^profile/edit/location/done/$', direct_to_template, { 'extra_context': { 'section': 'location' }, 'template': 'userprofile/profile/location_done.html'}),
    (r'^profile/edit/personal/done/$', direct_to_template, { 'extra_context': { 'section': 'personal' }, 'template': 'userprofile/profile/personal_done.html'}),
    (r'^profile/edit/public/done/$', direct_to_template, { 'extra_context': { 'section': 'public' }, 'template': 'userprofile/profile/makepublic_done.html'}),
    (r'^profile/delete/$', delete, { 'section': 'delete', 'template': 'userprofile/profile/delete.html'}),
    (r'^profile/delete/done/$', direct_to_template, { 'section': 'delete', 'template': 'userprofile/profile/delete_done.html'}),
    (r'^profile/edit/public/$', makepublic, { 'section': 'makepublic', 'APIKEY': APIKEY, 'template': 'userprofile/profile/makepublic.html'}),
    (r'^profile/edit/avatar/$', avatarchoose, { 'section': 'avatar', 'websearch': WEBSEARCH, 'template': 'userprofile/avatar/avatar_choose.html'}),
    (r'^profile/edit/avatar/delete/$', avatardelete),
    (r'^profile/edit/avatar/search/$', searchimages, { 'section': 'avatar', 'template': 'userprofile/avatar/avatar_search.html'}),
    (r'^profile/edit/avatar/crop/$', avatarcrop, { 'section': 'avatar', 'template': 'userprofile/avatar/avatar_crop.html'}),
    (r'^profile/edit/avatar/crop/done/$', direct_to_template, { 'section': 'avatar', 'template': 'userprofile/avatar/avatar_done.html'}),
    (r'^profile/getcountry_info/(?P<lat>[0-9\.\-]+)/(?P<lng>[0-9\.\-]+)/$', fetch_geodata),

    # Public profile
    (r'^profile/(?P<current_user>[a-zA-Z0-9\-_]*)/$', public, {'APIKEY': APIKEY, 'template': 'userprofile/profile/public.html'}),

    # Account utilities
    (r'^manage/$', overview, { 'section': 'overview', 'template' : 'userprofile/profile/overview.html'}),
    (r'^password/reset/$', reset_password, {'template' : 'userprofile/account/password_reset.html'}),
    (r'^email/validation/reset/$', email_validation_reset, {'template' : 'userprofile/account/email_validation_reset.html'}),
    (r'^email/validation/reset/done/(?P<action>success|failed)/$', direct_to_template, { 'extra_context': { 'section': 'overview' }, 'template' : 'userprofile/account/email_validation_reset_done.html'}),
    (r'^password/reset/done/$', direct_to_template, {'template': 'userprofile/account/password_reset_done.html'}),
    (r'^password/change/$', change_password_authenticated, { 'section': 'overview', 'template': 'userprofile/account/password_change.html'}),
    (r'^password/change/done/$', direct_to_template, { 'extra_context': {'section': 'overview'}, 'template': 'userprofile/account/password_change_done.html'}),
    (r'^password/change/(?P<key>.{70})/$', change_password_with_key, {'template': 'userprofile/account/password_change.html'}),
    (r'^email/validation/$', email_validation, { 'section': 'overview', 'template': 'userprofile/account/email_validation.html'}),
    (r'^email/validation/processed/$', direct_to_template, { 'extra_context': {'section': 'overview'}, 'template': 'userprofile/account/email_validation_processed.html'}),
    (r'^email/validation/(?P<key>.{70})/$', email_validation_process, { 'section': 'overview', 'template': 'userprofile/account/email_validation_done.html'}),
    (r'^login/$', views.login, {'template_name': 'userprofile/account/login.html'}),
    (r'^logout/$', logout, {'template': 'userprofile/account/logout.html'}),

    # Registration
    (r'^register/$', register, {'template' : 'userprofile/account/registration.html'}),
    (r'^register/validate/$', direct_to_template, {'template' : 'userprofile/account/validate.html'}),
    (r'^register/complete/$', direct_to_template, {'template': 'userprofile/account/registration_done.html'}),
)
