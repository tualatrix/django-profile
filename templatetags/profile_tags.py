from django.template import Library
from django.template.defaultfilters import stringfilter
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from profile.models import Profile,Avatar
from settings import MEDIA_URL
import datetime
import os.path

register = Library()

@register.inclusion_tag('profile/usercard.html')
def get_usercard(user):
    try:
        profile = user.get_profile()
    except:
        pass

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
        avatar_url = "%simages/default.gif" % MEDIA_URL

    path, extension = os.path.splitext(avatar_url)
    return  "%s.%s%s" % (path, width, extension)
