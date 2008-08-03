from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib.auth import views
from userprofile.views import *
from django.conf import settings

APIKEY = hasattr(settings, "APIKEY") and settings.APIKEY or None
WEBSEARCH = hasattr(settings, "WEBSEARCH") and settings.WEBSEARCH or None

urlpatterns = patterns('',
    # Private profile
    url(r'^profile/$', overview,
        {'section': 'overview', 'APIKEY': APIKEY,
         'template': 'userprofile/profile/overview.html'},
        name='profile_overview'),

    url(r'^profile/for/(?P<username>.+)/$', overview,
        {'section': 'overview', 'APIKEY': APIKEY,
         'template': 'userprofile/profile/overview.html'},
        name='profile_overview'),

    url(r'^profile/edit/(?P<section>location)/$', location,
        {'APIKEY': APIKEY, 'template': 'userprofile/profile/location.html'},
        name='profile_edit_location'),

    url(r'^profile/edit/(?P<section>personal)/$', personal,
        {'template': 'userprofile/profile/personal.html'},
        name='profile_edit_personal'),

    url(r'^profile/edit/location/done/$', direct_to_template,
        {'extra_context': {'section': 'location'},
        'template': 'userprofile/profile/location_done.html'},
        name='profile_edit_location_done'),

    url(r'^profile/edit/personal/done/$', direct_to_template,
        {'extra_context': {'section': 'personal'},
        'template': 'userprofile/profile/personal_done.html'},
        name='profile_edit_personal_done'),

    url(r'^profile/edit/public/$', makepublic,
        {'section': 'makepublic', 'APIKEY': APIKEY,
         'template': 'userprofile/profile/makepublic.html'},
        name='profile_edit_public'),

    url(r'^profile/edit/public/done/$', direct_to_template,
        {'extra_context': {'section': 'public'},
        'template': 'userprofile/profile/makepublic_done.html'},
        name='profile_edit_public_done'),

    url(r'^profile/delete/$', delete,
        {'section': 'delete', 'template': 'userprofile/profile/delete.html'},
        name='profile_delete'),

    url(r'^profile/delete/done/$', direct_to_template,
        {'section': 'delete',
         'template': 'userprofile/profile/delete_done.html'},
        name='profile_delete_done'),

    url(r'^profile/edit/avatar/$', avatarchoose,
        {'section': 'avatar', 'websearch': WEBSEARCH,
         'template': 'userprofile/avatar/choose.html'},
        name='profile_edit_avatar'),

    url(r'^profile/edit/avatar/delete/$', avatardelete,
        name='profile_avatar_delete'),

    url(r'^profile/edit/avatar/search/$', searchimages,
        {'section': 'avatar', 'template': 'userprofile/avatar/search.html'},
        name='profile_avatar_search'),

    url(r'^profile/edit/avatar/crop/$', avatarcrop,
        {'section': 'avatar', 'template': 'userprofile/avatar/crop.html'},
        name='profile_avatar_crop'),

    url(r'^profile/edit/avatar/crop/done/$', direct_to_template,
        {'section': 'avatar', 'template': 'userprofile/avatar/done.html'},
        name='profile_avatar_crop_done'),

    url(r'^profile/getcountry_info/(?P<lat>[0-9\.\-]+)/(?P<lng>[0-9\.\-]+)/$',
        fetch_geodata,
        name='profile_geocountry_info'),


    # Public profile
    url(r'^profile/(?P<current_user>[a-zA-Z0-9\-_]*)/$', public,
        {'APIKEY': APIKEY, 'template': 'userprofile/profile/public.html'},
        name=''),


    # Account utilities
    url(r'^manage/$', overview,
        {'section': 'overview',
         'template' : 'userprofile/profile/overview.html'},
        name='account_overview'),

    url(r'^password/reset/$', reset_password,
        {'template' : 'userprofile/account/password_reset.html'},
        name='password_reset'),

    url(r'^password/reset/done/$', direct_to_template,
        {'template': 'userprofile/account/password_reset_done.html'},
        name='password_reset_done'),

    url(r'^email/validation/$', email_validation,
        {'section': 'overview',
         'template': 'userprofile/account/email_validation.html'},
        name='email_validation'),

    url(r'^email/validation/processed/$', direct_to_template,
        {'extra_context': {'section': 'overview'},
         'template': 'userprofile/account/email_validation_processed.html'},
         name='email_validation_processed'),

    url(r'^email/validation/(?P<key>.{70})/$', email_validation_process,
        {'section': 'overview',
         'template': 'userprofile/account/email_validation_done.html'},
        name='email_validation_process'),

    url(r'^email/validation/reset/$', email_validation_reset,
        {'template' : 'userprofile/account/email_validation_reset.html'},
        name='email_validation_reset'),

    url(r'^email/validation/reset/done/(?P<action>success|failed)/$',
        direct_to_template, {'extra_context': {'section': 'overview'},
        'template' : 'userprofile/account/email_validation_reset_done.html'},
        name='email_validation_reset_done'),

    url(r'^password/change/$', change_password_authenticated,
        {'section': 'overview',
         'template': 'userprofile/account/password_change.html'},
        name='password_change'),

    url(r'^password/change/done/$', direct_to_template,
        {'extra_context': {'section': 'overview'},
         'template': 'userprofile/account/password_change_done.html'},
        name='password_change_done'),

    url(r'^password/change/(?P<key>.{70})/$', change_password_with_key,
        {'template': 'userprofile/account/password_change.html'},
        name='password_change_with_key'),

    url(r'^login/$', views.login,
        {'template_name': 'userprofile/account/login.html'},
        name='login'),

    url(r'^logout/$', logout,
        {'template': 'userprofile/account/logout.html'},
        name='logout'),


    # Registration
    url(r'^register/$', register,
        {'template' : 'userprofile/account/registration.html'},
        name='signup'),

    url(r'^register/validate/$', direct_to_template,
        {'template' : 'userprofile/account/validate.html'},
        name='signup_validate'),

    url(r'^register/complete/$', direct_to_template,
        {'template': 'userprofile/account/registration_done.html'},
        name='signup_complete'),
)
