from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import ugettext as _
from userprofile.forms import AvatarForm, AvatarCropForm, LocationForm, ProfileForm, UserForm, changePasswordAuthForm, ValidationForm, changePasswordKeyForm, EmailChangeForm
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.utils import simplejson
from django.contrib.auth.models import User
from userprofile.models import Profile, Continent, Country, Validation
from django.template import RequestContext
from django.core.validators import email_re
from django.conf import settings
import urllib2
import random
import pickle
import gdata.service
import os.path
import Image, ImageFilter
import urllib
from xml.dom import minidom
import os

if settings.WEBSEARCH:
    import gdata.photos.service

def get_profiles():
    return Profile.objects.order_by("-date")

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
        profile = User.objects.get(username=current_user).get_profile()
    except:
        raise Http404

    return render_to_response(template, locals(), context_instance=RequestContext(request))

@login_required
def makepublic(request, template, APIKEY, section):
    profile, created = Profile.objects.get_or_create(user = request.user)
    if request.method == "POST":
        public = dict()
        for item in profile.__dict__.keys():
            if request.POST.has_key("%s_public" % item):
                public[item] = request.POST.get("%s_public" % item)
        profile.save_public_file("%s.public" % profile.user, pickle.dumps(public))
        return HttpResponseRedirect("%sdone/" % request.path)

    return render_to_response(template, locals(), context_instance=RequestContext(request))

@login_required
def searchimages(request, template, section):
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
def overview(request, template, APIKEY, section):
    profile, created = Profile.objects.get_or_create(user=request.user)
    print "hola"
    validated = False
    try:
        email = Validation.objects.get(user=request.user).email
    except Validation.DoesNotExist:
        email = request.user.email
        if email: validated = True

    return render_to_response(template, locals(), context_instance=RequestContext(request))

@login_required
def profile(request, template, section, APIKEY=None):
    """
    Private part of the user profile
    """
    forms = { 'location': LocationForm, 'personal': ProfileForm }
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = forms[section](request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("%sdone/" % request.path)
    else:
        form = forms[section](instance=profile)

    lat = profile.latitude
    lng = profile.longitude

    continents = Continent.objects.all()
    country_data = dict()
    for continent in continents:
        country_data[continent] = Country.objects.filter(continent=continent)

    return render_to_response(template, locals(), context_instance=RequestContext(request))

@login_required
def save(request, section):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method=="POST":
        profile = Profile.objects.get(user=request.user)
        form = forms[section](request.POST, instance=profile)
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
def delete(request, template, section):
    user = User.objects.get(username=str(request.user))
    if request.method == "POST":
        # Remove the profile
        Profile.objects.get(user=user).delete()

        Validation.objects.filter(user=user).delete()

        # Remove the e-mail of the account too
        user.email = ''
        user.first_name = ''
        user.last_name = ''
        user.save()

        return HttpResponseRedirect('%sdone/' % request.path)

    return render_to_response(template, locals(), context_instance=RequestContext(request))

@login_required
def avatarchoose(request, template, section, websearch=False):
    """
    Avatar choose
    """
    profile, created = Profile.objects.get_or_create(user = request.user)
    if not request.method == "POST":
        form = AvatarForm()
    else:
        form = AvatarForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.cleaned_data.get('photo')
            url = form.cleaned_data.get('url')
            if url:
                photo = urllib2.urlopen(url).read()
            else:
                photo = photo.content
            profile.save_avatartemp_file("%s_temp.jpg" % request.user.username, photo)
            image = Image.open(profile.get_avatartemp_filename())
            image.thumbnail((800, 800), Image.ANTIALIAS)
            image.save(profile.get_avatartemp_filename(), "JPEG")
            profile.save()
            return HttpResponseRedirect('%scrop/' % request.path)

    return render_to_response(template, locals(), context_instance=RequestContext(request))

@login_required
def avatarcrop(request, template, section):
    """
    Avatar management
    """
    profile = Profile.objects.get(user = request.user)
    if not request.method == "POST":
        form = AvatarCropForm()
    else:
        form = AvatarCropForm(request.POST)
        if form.is_valid():
            top = int(request.POST.get('top'))
            left = int(request.POST.get('left'))
            right = int(request.POST.get('right'))
            bottom = int(request.POST.get('bottom'))

            image = Image.open(profile.get_avatartemp_filename())
            box = [ left, top, right, bottom ]
            image = image.crop(box)
            if image.mode not in ('L', 'RGB'):
                image = image.convert('RGB')

            base, temp = os.path.split(profile.get_avatartemp_filename())
            image.save(os.path.join(base, "%s.jpg" % profile.user.username))
            profile.avatar = os.path.join(os.path.split(profile.avatartemp)[0], "%s.jpg" % profile.user.username)
            for size in [ 96, 64, 32, 16 ]:
                image.thumbnail((size, size), Image.ANTIALIAS)
                image.save(os.path.join(base, "%s.%s.jpg" % (profile.user.username, size)))
                setattr(profile, "avatar%s" % size, os.path.join(os.path.split(profile.avatartemp)[0], "%s.%s.jpg" % (profile.user.username, size)))
            profile.save()
            return HttpResponseRedirect("%sdone/" % request.path)

    return render_to_response(template, locals(), context_instance=RequestContext(request))

@login_required
def avatardelete(request, avatar_id=False):
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

def json_error_response(error_message, *args, **kwargs):
    return HttpResponse(simplejson.dumps(dict(success=False,
                                              error_message=error_message), ensure_ascii=False))

@login_required
def change_email_with_key(request, key, template, section):
    """
    Verify key and change email
    """
    if Validation.objects.verify(key=key):
        message = _('E-mail changed successfully.')
        successful = True
    else:
        message = _('The key you received via e-mail is no longer valid. Please try the e-mail change process again.')
        successful = False

    return render_to_response(template, locals(), context_instance=RequestContext(request))

def email_validation_with_key(request, key, template):
    """
    Validate the e-mail of an account and activate it
    """
    if Validation.objects.verify(key=key):
        message = _('Account validated successfully. Now you can access to the login page with your username and password and start using this site.')
        successful = True
    else:
        message = _('The key you received via e-mail is no longer valid. Please try the e-mail validation process again.')
        successful = False

    return render_to_response(template, locals(), context_instance=RequestContext(request))

def email_change(request, template, section):
    """
    Change the e-mail page
    """
    if request.method == 'POST':
        form = EmailChangeForm(request.POST)
        if form.is_valid():
            Validation.objects.add(user=request.user, email=form.cleaned_data.get('email'), type="email")
            return HttpResponseRedirect('%sprocessed/' % request.path)
    else:
        form = EmailChangeForm()

    return render_to_response(template, locals(), context_instance=RequestContext(request))

def register(request, template):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            newuser = User.objects.create_user(username=username, email='', password=password)

            if form.cleaned_data.get('email'):
                newuser.email = form.cleaned_data.get('email')
                Validation.objects.add(user=newuser, email=newuser.email, type="email")

            newuser.save()
            return HttpResponseRedirect('%scomplete/' % request.path)
    else:
        form = UserForm()

    return render_to_response(template, locals(), context_instance=RequestContext(request))

def reset_password(request, template):
    if request.method == 'POST':
        form = ValidationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = User.objects.get(email=email)

            if email and user:
                Validation.objects.add(user=user, email=email, type="passwd")
                return HttpResponseRedirect('%sdone/' % request.path)

    else:
        form = ValidationForm()

    return render_to_response(template, locals(), context_instance=RequestContext(request))

def validation_reset(request, template):
    if request.user.is_authenticated():
        try:
            resend = Validation.objects.get(user=request.user).resend()
        except Validation.DoesNotExist:
            resend = False
        return HttpResponseRedirect('%sdone/%s' % (request.path, resend and 'success' or 'failed'))

    if request.method == 'POST':
        form = ValidationResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            resend = Validation.objects.get(email=email).resend()
            return HttpResponseRedirect('%sdone/%s' % (request.path, resend and 'success' or 'failed'))

    else:
        form = ValidationForm()

    return render_to_response(template, locals(), context_instance=RequestContext(request))

def change_password_with_key(request, key, template):
    """
    Change a user password with the key sended by e-mail
    """

    if not Validation.objects.verify(key=key):
        return render_to_response('userprofile/password_expired.html', context_instance=RequestContext(request))

    user = Validation.objects.getuser(key=key)
    if request.method == "POST":
        form = changePasswordKeyForm(request.POST)
        if form.is_valid():
            form.save(key)
            return HttpResponseRedirect('/accounts/password/change/done/')
    else:
        form = changePasswordKeyForm()

    return render_to_response(template, locals(), context_instance=RequestContext(request))

@login_required
def change_password_authenticated(request, template, section):
    """
    Change the password of the authenticated user
    """
    if request.method == "POST":
        form = changePasswordAuthForm(request.POST)
        if form.is_valid():
            form.save(request.user)
            return HttpResponseRedirect('%sdone/' % request.path)
    else:
        form = changePasswordAuthForm()

    return render_to_response(template, locals(), context_instance=RequestContext(request))

def check_user(request, user):
    """
    Check if a username exists. Only HTTPXMLRequest. Returns JSON
    """
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        if len(user) < 3 or not set(user).issubset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_") or User.objects.filter(username__iexact=user).count() > 0:
            return json_error_response(simplejson.dumps({'success': False}))
        else:
            return HttpResponse(simplejson.dumps({'success': True}))
    else:
        raise Http404

def check_email_unused(request, email):
    """
    Check if an e-mail exists. Only HTTPXMLRequest. Returns JSON
    """
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        if not email_re.search(email):
            return json_error_response(_("Invalid e-mail"))

        if not User.objects.filter(email=email) and not Validation.objects.filter(email=email):
            return HttpResponse(simplejson.dumps({'success': True}))
        else:
            return json_error_response(_("E-mail not registered"))
    else:
        raise Http404

def check_email(request, email):
    """
    Check if a username exists. Only HTTPXMLRequest. Returns JSON
    """
    try:
        User.objects.get(email=email)
        return HttpResponse(simplejson.dumps({'success': True}))
    except User.DoesNotExist:
        return json_error_response(_("E-mail not registered"))

def check_validating_email(request, email):
    """
    Check if a username exists. Only HTTPXMLRequest. Returns JSON
    """
    try:
        Validation.objects.get(email=email)
        return HttpResponse(simplejson.dumps({'success': True}))
    except Validation.DoesNotExist:
        return json_error_response(_("E-mail not registered"))


def logout(request, template):
    from django.contrib.auth import logout
    logout(request)
    return render_to_response(template, locals(), context_instance=RequestContext(request))

