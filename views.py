from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from forms import ProfileForm, AvatarForm
from models import Profile
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.utils import simplejson
from django.contrib.auth.models import User
from profile.models import Avatar, Profile, Continent, Country
from account.models import EmailValidate
import random
import Image, ImageFilter
import urllib
from xml.dom import minidom
import os

IMSIZES = ( 128, 96, 64, 32, 16 )

def fetch_geodata(request, lat, lng):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        url = "http://ws.geonames.org/countrySubdivision?lat=%s&lng=%s" % (lat, lng)
        dom = minidom.parse(urllib.urlopen(url))
        country = dom.getElementsByTagName('countryCode')
        if len(country) >=1:
            country = country[0].childNodes[0].data
        region = dom.getElementsByTagName('adminName1')
        if len(region) >=1:
            region = region[0].childNodes[0].data

        return HttpResponse(simplejson.dumps({'success': True, 'country': country, 'region': region}))
    else:
        raise Http404()

def public(request, user, template):
    cuser = User.objects.get(username=user)
    try:
        profile = cuser.get_profile()
        avatar = Avatar.objects.get(user=cuser, valid=True)
    except:
        pass
    user = request.user

    return render_to_response(template, locals())

@login_required
def private(request, APIKEY, template):
    """
    Private part of the user profile
    """
    apikey = APIKEY
    user = User.objects.get(username=str(request.user))
    profile, created = Profile.objects.get_or_create(user = user)

    try:
        email = EmailValidate.objects.get(user=user).email
        validated = False
    except:
        email = user.email
        validated = True

    try:
        avatar = Avatar.objects.filter(user=user, valid=True)[0]
    except:
        pass

    if request.method == "POST" and form.is_valid():
        form = ProfileForm(request.POST, request.FILES)
    else:
        form = ProfileForm()

    lat = profile.latitude
    lng = profile.longitude

    continents = Continent.objects.all()
    country_data = dict()
    for continent in continents:
        country_data[continent] = Country.objects.filter(continent=continent)

    return render_to_response(template, locals())

@login_required
def save(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        form = ProfileForm(request)
        if request.method == "POST" and form.is_valid():
            form.save()
            return HttpResponse(simplejson.dumps({'success': True}))
        else:
            return HttpResponse(simplejson.dumps({'success': False, 'error': form.errors}))
    else:
        raise Http404()

@login_required
def delete(request, template):
    user = User.objects.get(username=str(request.user))
    if request.method == "POST":
        # Remove the profile
        try:
            Profile.objects.get(user=user).delete()
        except:
            pass
        # Remove the avatar if exists
        try:
            Avatar.objects.get(user=user).delete()
        except:
            pass

        # Remove the e-mail of the account too
        user.email = ''
        user.save()

        return HttpResponseRedirect('%sdone/' % request.path)

    return render_to_response(template, locals())

@login_required
def avatar(request, template, step="one"):
    """
    Avatar management
    """
    if not request.method == "POST":
        form = AvatarForm()
    else:
        if step=="one":
            form = AvatarForm(request.POST, request.FILES)
            if form.is_valid():
                data = form.cleaned_data.get('photo')
                Avatar.objects.filter(user=request.user, valid=False).delete()
                avatar = Avatar(user=request.user)
                avatar.save_photo_file("%s%s" % (request.user.username, data.get('extension')), data['photo'].content)
                avatar.save()

                width = avatar.get_photo_width()
                height = avatar.get_photo_height()
                if width < 96 or height < 96:
                    cropsize = 32
                else:
                    cropsize = 96

                cx = width/2 - 48
                if cx < 0: cx=0
                cy = height/2 - 48
                if cy < 0: cy=0

        elif step=="two":
            avatar = Avatar.objects.get(user = request.user, pk = request.POST.get('avatar_id'))
            avatar.valid = True
            if request.POST.get('top') and request.POST.get('left') and request.POST.get('size'):
                top = request.POST.get('top')
                left = request.POST.get('left')
                size = request.POST.get('size')
                avatar.box = "%s-%s-%s-%s" % ( int(left), int(top), int(left) + int(size), int(top) + int(size))

            avatar.save()
            done = True

    return render_to_response(template, locals())

@login_required
def avatarDelete(request, avatar_id=False):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        try:
            avatar = Avatar.objects.get(user=request.user)
            avatar.delete()
        except:
            pass
        return HttpResponse(simplejson.dumps({'success': True}))
    else:
        raise Http404()
