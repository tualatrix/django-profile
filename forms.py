from django import newforms as forms
from django.core.exceptions import ObjectDoesNotExist
from userprofile.models import Profile, GENDER_CHOICES
from django.utils.translation import ugettext as _
from userprofile.models import Country

IMAGE_TYPES = { 'JPEG image data': '.jpg', 'PNG image data': '.png', 'GIF image data': '.gif' }

class ProfileForm(forms.ModelForm):
    """
    Profile Form. Composed by all the Profile model fields.
    """

    class Meta:
        model = Profile
        exclude = ('user', 'slug', 'public', 'date', 'avatartemp', 'avatar', 'avatar16', 'avatar32', 'avatar64', 'avatar96')

class AvatarForm(forms.Form):
    """
    The avatar form requires only one image field.
    """
    avatar = forms.ImageField(required=False)
    url = forms.URLField(required=False)

    def clean(self):
        if not (self.cleaned_data.get('avatar') or self.cleaned_data.get('url')):
            raise forms.ValidationError(_('You must enter one of the options'))
        else:
            return self.cleaned_data

class AvatarCropForm(forms.Form):
    """
    Crop dimensions form
    """
    top = forms.IntegerField()
    bottom = forms.IntegerField()
    left = forms.IntegerField()
    right = forms.IntegerField()

