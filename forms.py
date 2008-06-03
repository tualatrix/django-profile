from django import newforms as forms
from django.core.exceptions import ObjectDoesNotExist
from userprofile.models import Profile, Avatar, GENDER_CHOICES
from django.utils.translation import ugettext as _
from userprofile.models import Country

IMAGE_TYPES = { 'JPEG image data': '.jpg', 'PNG image data': '.png', 'GIF image data': '.gif' }

class ProfileForm(forms.ModelForm):
    """
    Profile Form. Composed by all the Profile model fields.
    """

    class Meta:
        model = Profile
        exclude = ('user', 'slug', 'date')

class AvatarForm(forms.Form):
    """
    The avatar form requires only one image field.
    """
    photo = forms.ImageField()

class AvatarCropForm(forms.Form):
    """
    Crop dimensions form
    """
    top = forms.IntegerField()
    bottom = forms.IntegerField()
    left = forms.IntegerField()
    right = forms.IntegerField()

