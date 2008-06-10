from django.template import Library
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
