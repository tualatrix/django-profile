from django.template import Library
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from profile.models import Profile,Avatar
import datetime
import os.path

register = Library()

@register.inclusion_tag('profile/usercard.html')
def get_usercard(profile):
    gender = { "M": "/site_media/images/male.png", "F": "/site_media/images/female.png" }
    profile = profile
    user = profile.user

    if profile.gender:
        gender_img = gender.get(profile.gender)

    if profile.birthdate.year < datetime.datetime.now().year:
        yearsold = profile.yearsold()

    try:
        avatar = Avatar.objects.get(user=user)
        if avatar.get_photo_filename() and os.path.isfile(avatar.get_photo_filename()):
            avatar_url = avatar.get_absolute_url()
        else:
            raise Exception()
    except:
        avatar_url = "/site_media/images/default.gif"

    return locals()

