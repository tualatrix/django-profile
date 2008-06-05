from django.template import Library
from django.template.defaultfilters import stringfilter
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from userprofile.models import Profile
from django.conf import settings
import datetime
import os.path

register = Library()

@register.inclusion_tag('userprofile/usercard.html')
def get_usercard(user):
    profile, created = Profile.objects.get_or_create(user=user)
    return locals()

@register.filter
@stringfilter
def avatar(user, width):
    user = User.objects.get(username=user)
    try:
        profile = Profile.objects.get(user = user)
        return profile.avatar
    except:
        avatar_url = "%simages/default.gif" % settings.MEDIA_URL

    path, extension = os.path.splitext(avatar_url)
    return  "%s.%s%s" % (path, width, extension)
