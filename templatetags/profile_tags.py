from django.template import Library
from django.template.defaultfilters import stringfilter
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from profile.models import Profile,Avatar
import datetime
import os.path

register = Library()

@register.inclusion_tag('profile/mini_usercard.html')
def get_miniusercard(profile, manage=False):
    try:
        avatar = Avatar.objects.get(user=user)
        if avatar.get_photo_filename() and os.path.isfile(avatar.get_photo_filename()):
            avatar_url = avatar.get_absolute_url()
        else:
            raise Exception()
    except:
        avatar_url = "/site_media/images/default.gif"

    return locals()

@register.inclusion_tag('profile/usercard.html')
def get_usercard(profile):
    gender = { "M": "/site_media/images/male.png", "F": "/site_media/images/female.png" }
    profile = profile
    user = profile.user

    if profile.gender:
        gender_img = gender.get(profile.gender)

    if profile.birthdate.year < datetime.datetime.now().year:
        yearsold = profile.yearsold()

    return locals()

@register.filter
@stringfilter
def avatar(user, width):
    user = User.objects.get(username=user)
    try:
        if type(user) == type(u"") or type(user) == type(""):
            user = User.objects.get(username=user)

        avatar = Avatar.objects.get(user=user)
        if avatar.get_photo_filename() and os.path.isfile(avatar.get_photo_filename()):
            avatar_url = avatar.get_absolute_url()
        else:
            raise Exception()
    except:
        avatar_url = "/site_media/images/default.gif"

    path, extension = os.path.splitext(avatar_url)
    return  "%s.%s%s" % (path, width, extension)
