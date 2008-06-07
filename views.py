from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from userprofile.forms import ProfileForm, AvatarForm, AvatarCropForm
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.utils import simplejson
from django.contrib.auth.models import User
from userprofile.models import Profile, Continent, Country
from account.models import Validation
from django.template import RequestContext
from django.conf import settings
import urllib2
import random
import pickle
import gdata.service
import gdata.photos.service
import Image, ImageFilter
import urllib
from xml.dom import minidom
import os

IMSIZES = ( 128, 96, 64, 32, 24, 16 )

def valid_users():
    return User.objects.filter(is_active=True).order_by("-date_joined")

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

def public(request, APIKEY, current_user, template):
    try:
        profile = User.objects.get(username=current_user, is_active=True).get_profile()
    except:
        raise Http404

    return render_to_response(template, locals(), context_instance=RequestContext(request))

@login_required
def searchimages(request, template):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method=="POST" and request.POST.get('search'):
        photos = list()
        urls = list()
        gd_client = gdata.photos.service.PhotosService()
        feed = gd_client.SearchCommunityPhotos("%s&thumbsize=72c" % request.POST.get('search').split(" ")[0], limit='35')
        for entry in feed.entry:
            photos.append(entry.media.thumbnail[0].url)
            urls.append(entry.content.src)
        return HttpResponse(simplejson.dumps({'success': True, 'photos': photos, 'urls': urls }))
    else:
        return render_to_response(template, locals(), context_instance=RequestContext(request))


@login_required
def private(request, APIKEY, template):
    """
    Private part of the user profile
    """
    profile, created = Profile.objects.get_or_create(user = request.user)

    try:
        email = Validation.objects.get(user=user).email
        validated = False
    except:
        email = request.user.email
        validated = True

    if request.method == "POST" and form.is_valid():
        form = ProfileForm(request.POST, instance=profile)
    else:
        form = ProfileForm(instance=profile)

    lat = profile.latitude
    lng = profile.longitude

    continents = Continent.objects.all()
    country_data = dict()
    for continent in continents:
        country_data[continent] = Country.objects.filter(continent=continent)

    return render_to_response(template, locals(), context_instance=RequestContext(request))

@login_required
def save(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method=="POST":
        profile = Profile.objects.get(user=request.user)
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save()

            public = dict()
            for item in profile.__dict__.keys():
                if request.POST.has_key("%s_public" % item):
                    public[item] = request.POST.get("%s_public" % item)
            profile.save_public_file("%s.public" % profile.user, pickle.dumps(public))
            return HttpResponse(simplejson.dumps({'success': True}))
        else:
            return HttpResponse(simplejson.dumps({'success': False }))
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

        # Remove the e-mail of the account too
        user.email = ''
        user.first_name = ''
        user.last_name = ''
        user.save()

        return HttpResponseRedirect('%sdone/' % request.path)

    return render_to_response(template, locals(), context_instance=RequestContext(request))

@login_required
def avatarChoose(request, template):
    """
    Avatar choose
    """
    if not request.method == "POST":
        form = AvatarForm()
    else:
        form = AvatarForm(request.POST, request.FILES)
        if form.is_valid():
            profile = Profile.objects.get(user = request.user)
            photo = form.cleaned_data.get('photo')
            url = form.cleaned_data.get('url')
            if url:
                photo = urllib2.urlopen(url).read()
            profile.save_avatartemp_file("%s.jpg" % request.user.username, photo)
            #image = Image.open(profile.get_avatartemp_filename())
            #image.thumbnail((500, 500), Image.ANTIALIAS)
            #image.save(profile.get_avatartemp_filename(), "JPEG")
            profile.save()

    return render_to_response(template, locals(), context_instance=RequestContext(request))

@login_required
def avatarCrop(request, template):
    """
    Avatar management
    """
    if not request.method == "POST":
        raise Http404()

    form = AvatarCropForm(request.POST)
    if form.is_valid():
        profile = Profile.objects.get(user = request.user)
        top = int(request.POST.get('top'))
        left = int(request.POST.get('left'))
        right = int(request.POST.get('right'))
        bottom = int(request.POST.get('bottom'))
        if top < 0: top = 0
        if left < 0: left = 0

        image = Image.open(profile.get_avatartemp_filename())
        box = [ left, top, right, bottom ]
        image = image.crop(box)
        if image.mode not in ('L', 'RGB'):
            image = image.convert('RGB')

        filename = profile.get_avatartemp_filename()
        os.remove(filename)
        profile.avatartemp = ''
        image.save("%s.jpg" % filename, "JPEG")
        profile.avatar = filename
        for size in [ '96', '64', '32', '16' ]:
            image.thumbnail((size, size), Image.ANTIALIAS)
            image.save("%s.%s.jpg" % (filename, size), "JPEG")
            setattr(profile, "avatar%s" % size, "%s.%s.jpg" % (filename, size))
        del image
        profile.save()
        done = True

    return render_to_response(template, locals(), context_instance=RequestContext(request))

@login_required
def avatarDelete(request, avatar_id=False):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        profile = Profile.objects.get(user = request.user)
        for key in [ '', 'temp', '16', '32', '64', '96' ]:
            try:
                os.remove("%s" % getattr(profile, "get_avatar%s_filename" % key)())
            except:
                pass
            setattr(profile, "avatar%s" % key, '')
        profile.save()
        return HttpResponse(simplejson.dumps({'success': True}))
    else:
        raise Http404()
