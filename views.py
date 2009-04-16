from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from userprofile.forms import AvatarForm, AvatarCropForm, EmailValidationForm, \
                              ProfileForm, RegistrationForm, LocationForm, \
                              ResendEmailValidationForm, PublicFieldsForm
from userprofile.models import BaseProfile
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.db import models
from django.contrib.auth.models import User, SiteProfileNotAvailable
from userprofile.models import EmailValidation, Avatar, UserProfileMediaNotFound, \
                               GoogleDataAPINotFound
from django.template import RequestContext
from django.conf import settings
from xml.dom import minidom
import urllib2
import random
import cPickle as pickle
import base64
import urllib
import os

if hasattr(settings, "AVATAR_QUOTA"):
    from userprofile.uploadhandler import QuotaUploadHandler

try:
    from PIL import Image
except ImportError:
    import Image

if not settings.AUTH_PROFILE_MODULE:
    raise SiteProfileNotAvailable
try:
    app_label, model_name = settings.AUTH_PROFILE_MODULE.split('.')
    Profile = models.get_model(app_label, model_name)
except (ImportError, ImproperlyConfigured):
    raise SiteProfileNotAvailable

if not Profile:
    raise SiteProfileNotAvailable

if not os.path.isdir(os.path.join(settings.MEDIA_ROOT, "userprofile")):
    raise UserProfileMediaNotFound

if hasattr(settings, "DEFAULT_AVATAR") and settings.DEFAULT_AVATAR:
    DEFAULT_AVATAR = settings.DEFAULT_AVATAR
else:
    DEFAULT_AVATAR = os.path.join(settings.MEDIA_ROOT, "userprofile/generic.jpg")

GOOGLE_MAPS_API_KEY = hasattr(settings, "GOOGLE_MAPS_API_KEY") and \
                      settings.GOOGLE_MAPS_API_KEY or None
AVATAR_WEBSEARCH = hasattr(settings, "AVATAR_WEBSEARCH") and \
                   settings.AVATAR_WEBSEARCH or None

if AVATAR_WEBSEARCH:
    try:
        import gdata.service
        import gdata.photos.service
    except:
        raise GoogleDataAPINotFound

def get_profiles():
    return Profile.objects.order_by("-creation_date")

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

def public(request, username):
    try:
        profile = User.objects.get(username=username).get_profile()
    except:
        raise Http404

    template = "userprofile/profile/public.html"
    data = { 'profile': profile, 'GOOGLE_MAPS_API_KEY': GOOGLE_MAPS_API_KEY, }
    return render_to_response(template, data, context_instance=RequestContext(request))

@login_required
def overview(request):
    """
    Main profile page
    """
    profile, created = Profile.objects.get_or_create(user=request.user)
    validated = False
    try:
        email = EmailValidation.objects.get(user=request.user).email
    except EmailValidation.DoesNotExist:
        email = request.user.email
        if email: validated = True

    fields = [{ 
        'name': f.name, 
        'verbose_name': f.verbose_name, 
        'value': getattr(profile, f.name)
    } for f in Profile._meta.fields if not (f in BaseProfile._meta.fields or f.name=='id')]

    template = "userprofile/profile/overview.html"
    data = { 'section': 'overview', 'GOOGLE_MAPS_API_KEY': GOOGLE_MAPS_API_KEY,
            'email': email, 'validated': validated, 'fields' : fields }
    return render_to_response(template, data, context_instance=RequestContext(request))

@login_required
def personal(request):
    """
    Personal data of the user profile
    """
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            request.user.message_set.create(message=_("Your profile information has been updated successfully."))
    else:
        form = ProfileForm(instance=profile)

    template = "userprofile/profile/personal.html"
    data = { 'section': 'personal', 'GOOGLE_MAPS_API_KEY': GOOGLE_MAPS_API_KEY,
             'form': form, }
    return render_to_response(template, data, context_instance=RequestContext(request))

@login_required
def location(request):
    """
    Location selection of the user profile
    """
    profile, created = Profile.objects.get_or_create(user=request.user)
    geoip = hasattr(settings, "GEOIP_PATH")
    if geoip and request.method == "GET" and request.GET.get('ip') == "1":
        from django.contrib.gis.utils import GeoIP
        g = GeoIP()
        c = g.city(request.META.get("REMOTE_ADDR"))
        if c and c.get("latitude") and c.get("longitude"):
            profile.latitude = "%.6f" % c.get("latitude")
            profile.longitude = "%.6f" % c.get("longitude")
            profile.country = c.get("country_code")
            profile.location = unicode(c.get("city"), "latin1")

    if request.method == "POST":
        form = LocationForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            request.user.message_set.create(message=_("Your profile information has been updated successfully."))
    else:
        form = LocationForm(instance=profile)

    template = "userprofile/profile/location.html"
    data = { 'section': 'location', 'GOOGLE_MAPS_API_KEY': GOOGLE_MAPS_API_KEY,
             'form': form, 'geoip': geoip }
    return render_to_response(template, data, context_instance=RequestContext(request))

@login_required
def delete(request):
    if request.method == "POST":
        # Remove the profile and all the information
        Profile.objects.filter(user=request.user).delete()
        EmailValidation.objects.filter(user=request.user).delete()
        Avatar.objects.filter(user=request.user).delete()

        # Remove the e-mail of the account too
        request.user.email = ''
        request.user.first_name = ''
        request.user.last_name = ''
        request.user.save()

        request.user.message_set.create(message=_("Your profile information has been removed successfully."))
        return HttpResponseRedirect(reverse("profile_overview"))

    template = "userprofile/profile/delete.html"
    data = { 'section': 'delete', }
    return render_to_response(template, data, context_instance=RequestContext(request))

@login_required
def avatarchoose(request):
    """
    Avatar choose
    """
    profile, created = Profile.objects.get_or_create(user = request.user)
    images = dict()

    if hasattr(settings, "AVATAR_QUOTA"):
        request.upload_handlers.insert(0, QuotaUploadHandler())

    if request.method == "POST":
        form = AvatarForm()
        if request.POST.get('keyword'):
            keyword = str(request.POST.get('keyword'))
            gd_client = gdata.photos.service.PhotosService()
            feed = gd_client.SearchCommunityPhotos(query = "%s&thumbsize=72c" % keyword.split(" ")[0], limit='48')
            for entry in feed.entry:
                images[entry.media.thumbnail[0].url] = entry.content.src

        else:
            form = AvatarForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.cleaned_data.get('url') or form.cleaned_data.get('photo')
                avatar = Avatar(user=request.user, image=image, valid=False)
                avatar.image.save("%s.jpg" % request.user.username, image)
                image = Image.open(avatar.image.path)
                image.thumbnail((480, 480), Image.ANTIALIAS)
                image.convert("RGB").save(avatar.image.path, "JPEG")
                avatar.save()
                return HttpResponseRedirect(reverse("profile_avatar_crop"))

                base, filename = os.path.split(avatar_path)
                generic, extension = os.path.splitext(filename)
    else:
        form = AvatarForm()

    if DEFAULT_AVATAR:
        base, filename = os.path.split(DEFAULT_AVATAR)
        filename, extension = os.path.splitext(filename)
        generic96 = "%s/%s.96%s" % (base, filename, extension)
        generic96 = generic96.replace(settings.MEDIA_ROOT, settings.MEDIA_URL)
    else:
        generic96 = ""

    template = "userprofile/avatar/choose.html"
    data = { 'generic96': generic96, 'form': form, "images": images,
             'AVATAR_WEBSEARCH': AVATAR_WEBSEARCH, 'section': 'avatar', }
    return render_to_response(template, data, context_instance=RequestContext(request))

@login_required
def avatarcrop(request):
    """
    Avatar management
    """
    avatar = get_object_or_404(Avatar, user=request.user, valid=False)
    if not request.method == "POST":
        form = AvatarCropForm()
    else:
        image = Image.open(avatar.image.path)
        form = AvatarCropForm(image, request.POST)
        if form.is_valid():
            top = int(form.cleaned_data.get('top'))
            left = int(form.cleaned_data.get('left'))
            right = int(form.cleaned_data.get('right'))
            bottom = int(form.cleaned_data.get('bottom'))

            print top, left, right, bottom
            if not (top or left or right or bottom):
                (width, height) = image.size
                if width > height:
                    diff = (width-height) / 2
                    left = diff
                    right = width-diff
                    bottom = height
                else:
                    diff = (height-width) / 2
                    top = diff
                    right = width
                    bottom = height-diff

            box = [ left, top, right, bottom ]
            print box
            image = image.crop(box)
            if image.mode not in ('L', 'RGB'):
                image = image.convert('RGB')

            image.save(avatar.image.path)
            avatar.valid = True
            avatar.save()
            request.user.message_set.create(message=_("Your new avatar has been saved successfully."))
            return HttpResponseRedirect(reverse("profile_edit_avatar"))

    template = "userprofile/avatar/crop.html"
    data = { 'section': 'avatar', 'avatar': avatar, 'form': form, }
    return render_to_response(template, data, context_instance=RequestContext(request))

@login_required
def avatardelete(request, avatar_id=False):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        try:
            Avatar.objects.get(user=request.user, valid=True).delete()
            return HttpResponse(simplejson.dumps({'success': True}))
        except:
            return HttpResponse(simplejson.dumps({'success': False}))
    else:
        raise Http404()

def email_validation_process(request, key):
    """
    Verify key and change email
    """
    if EmailValidation.objects.verify(key=key):
        successful = True
    else:
        successful = False

    template = "userprofile/account/email_validation_done.html"
    data = { 'successful': successful, }
    return render_to_response(template, data, context_instance=RequestContext(request))

def email_validation(request):
    """
    E-mail Change form
    """
    if request.method == 'POST':
        form = EmailValidationForm(request.POST)
        if form.is_valid():
            EmailValidation.objects.add(user=request.user, email=form.cleaned_data.get('email'))
            return HttpResponseRedirect(reverse("email_validation_processed"))
    else:
        form = EmailValidationForm()

    template = "userprofile/account/email_validation.html"
    data = { 'form': form, }
    return render_to_response(template, data, context_instance=RequestContext(request))

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            newuser = User.objects.create_user(username=username, email='', password=password)
            newuser.is_active = not hasattr(settings, "REQUIRE_EMAIL_CONFIRMATION") or not settings.REQUIRE_EMAIL_CONFIRMATION

            if form.cleaned_data.get('email'):
                newuser.email = form.cleaned_data.get('email')
                EmailValidation.objects.add(user=newuser, email=newuser.email)

            newuser.save()
            return HttpResponseRedirect(reverse('signup_complete'))
    else:
        form = RegistrationForm()

    template = "userprofile/account/registration.html"
    data = { 'form': form, }
    return render_to_response(template, data, context_instance=RequestContext(request))

def email_validation_reset(request):
    """
    Resend the validation email
    """

    if request.user.is_authenticated():
        try:
            resend = EmailValidation.objects.get(user=request.user).resend()
            response = "done"
        except EmailValidation.DoesNotExist:
            response = "failed"

        return HttpResponseRedirect(reverse("email_validation_reset_response", args=[response]))
    else:
        if request.method == 'POST':
            form = ResendEmailValidationForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data.get('email')
                try:
                    resend = EmailValidation.objects.get(email=email).resend()
                    response = "done"
                except EmailValidation.DoesNotExist:
                    response = "failed"
                return HttpResponseRedirect(reverse("email_validation_reset_response", args=[response]))

        else:
            form = ResendEmailValidationForm()

        template = "userprofile/account/email_validation_reset.html"
        data = { 'form': form, }
        return render_to_response(template, data, context_instance=RequestContext(request))
