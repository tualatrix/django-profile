from django import newforms as forms
from django.core.exceptions import ObjectDoesNotExist
from profile.models import Profile, Avatar, GENDER_CHOICES
from django.utils.translation import ugettext as _
from profile.models import Country
import magic

IMAGE_TYPES = { 'JPEG image data': '.jpg', 'PNG image data': '.png', 'GIF image data': '.gif' }

class ProfileForm(forms.ModelForm):
    """
    Profile Form. Composed by all the Profile model fields.
    """

    class Meta:
        model = Profile
        exclude = ('user', 'date')

class AvatarForm(forms.Form):
    """
    The avatar form requires only one image field.
    """
    photo = forms.ImageField()

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        ms = magic.open(magic.MAGIC_NONE)
        ms.load()
        type = ms.buffer(photo.content)

        if not type.split(",")[0] in IMAGE_TYPES:
            raise forms.ValidationError(_('The file type is invalid: %s' % type))

        return { 'photo': photo, 'extension': IMAGE_TYPES.get(type.split(",")[0]) }

class AvatarCropForm(forms.Form):
    """
    Crop dimensions form
    """
    top = forms.IntegerField()
    bottom = forms.IntegerField()
    left = forms.IntegerField()
    right = forms.IntegerField()

