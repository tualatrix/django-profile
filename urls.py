from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib.auth import views
from userprofile.views import *
from django.conf import settings

urlpatterns = patterns('',
    # Private profile
    (r'^profile/$', overview, { 'section': 'overview', 'APIKEY': settings.APIKEY, 'template': 'userprofile/overview.html'}),
    (r'^profile/edit/(?P<section>location)/$', profile, {'APIKEY': settings.APIKEY, 'template': 'userprofile/location.html'}),
    (r'^profile/edit/(?P<section>personal)/$', profile, {'template': 'userprofile/personal.html'}),
    (r'^profile/edit/(?P<section>personal|location|public)/done/$', direct_to_template, {'template': 'userprofile/profile_done.html'}),
    (r'^profile/delete/$', delete, { 'section': 'delete', 'template': 'userprofile/delete.html'}),
    (r'^profile/delete/done/$', direct_to_template, { 'section': 'delete', 'template': 'userprofile/delete_done.html'}),
    (r'^profile/edit/public/$', makepublic, { 'section': 'makepublic', 'APIKEY': settings.APIKEY, 'template': 'userprofile/makepublic.html'}),
    (r'^profile/edit/avatar/$', avatarchoose, { 'section': 'avatar', 'websearch': settings.WEBSEARCH, 'template': 'userprofile/avatar_choose.html'}),
    (r'^profile/edit/avatar/delete/$', avatardelete),
    (r'^profile/edit/avatar/search/$', searchimages, { 'section': 'avatar', 'template': 'userprofile/avatar_search.html'}),
    (r'^profile/edit/avatar/crop/$', avatarcrop, { 'section': 'avatar', 'template': 'userprofile/avatar_crop.html'}),
    (r'^profile/edit/avatar/crop/done/$', direct_to_template, { 'section': 'avatar', 'template': 'userprofile/avatar_done.html'}),
    (r'^profile/getcountry_info/(?P<lat>[0-9\.\-]+)/(?P<lng>[0-9\.\-]+)/$', fetch_geodata),

    # Public profile
    (r'^profile/(?P<current_user>[a-zA-Z0-9\-_]*)/$', public, {'APIKEY': settings.APIKEY, 'template': 'userprofile/public.html'}),

    # Account utilities
    (r'^manage/$', overview, { 'section': 'overview', 'template' : 'userprofile/overview.html'}),
    (r'^password/reset/$', reset_password, {'template' : 'userprofile/password_reset.html'}),
    (r'^validation/reset/$', resend_validation, {'template' : 'userprofile/validation_reset.html'}),
    (r'^validation/reset/done/(?P<action>success|failed)/$', direct_to_template, {'template' : 'userprofile/validation_reset_done.html'}),
    (r'^password/reset/done/$', direct_to_template, {'template': 'userprofile/password_reset_done.html'}),
    (r'^password/change/$', change_password_authenticated, { 'section': 'overview', 'template': 'userprofile/password_change.html'}),
    (r'^password/change/done/$', direct_to_template, { 'extra_context': {'section': 'overview'}, 'template': 'userprofile/password_change_done.html'}),
    (r'^password/change/(?P<key>.{70})/$', change_password_with_key, {'template': 'userprofile/password_change.html'}),
    (r'^email/change/$', email_change, { 'section': 'overview', 'template': 'userprofile/email_change.html'}),
    (r'^email/change/processed/$', direct_to_template, { 'extra_context': {'section': 'overview'}, 'template': 'userprofile/email_change_processed.html'}),
    (r'^email/change/(?P<key>.{70})/$', change_email_with_key, { 'section': 'overview', 'template': 'userprofile/email_change_done.html'}),
    (r'^login/$', views.login, {'template_name': 'userprofile/login.html'}),
    (r'^logout/$', logout, {'template': 'userprofile/logout.html'}),
    (r'^check_user/(?P<user>.*)/$', check_user),
    (r'^check_email/(?P<email>.*)/$', check_email),
    (r'^check_email_unused/(?P<email>.*)/$', check_email_unused),
    (r'^validate/(?P<key>.{70})/$', email_validation_with_key, {'template': 'userprofile/email_validation.html'}),

    # Registration
    (r'^register/$', register, {'template' : 'userprofile/registration.html'}),
    (r'^register/validate/$', direct_to_template, {'template' : 'userprofile/validate.html'}),
    (r'^register/complete/$', direct_to_template, {'template': 'userprofile/registration_done.html'}),
)
