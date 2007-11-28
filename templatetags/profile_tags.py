from django.template import Library
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from profile.models import Profile

register = Library()

@register.inclusion_tag('profile/usercard.html')
def get_usercard(profile):
    print "hola"
    return { 'profile': profile }

