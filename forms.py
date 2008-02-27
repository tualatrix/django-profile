from django import newforms as forms
from django.core.exceptions import ObjectDoesNotExist
from profile.models import Profile, Avatar, GENDER_CHOICES
from profile.models import Country

class ProfileForm(forms.Form):
    """
    Profile Form. Composed by all the Profile model fields.
    """

    firstname = forms.CharField(max_length=255, required=False)
    surname = forms.CharField(max_length=255, required=False)
    birthdate = forms.DateTimeField(required=False)
    url = forms.URLField(verify_exists=True, required=False)
    about = forms.CharField(widget=forms.Textarea, required=False)
    latitude = forms.DecimalField(max_digits=8, decimal_places=6, required=False)
    longitude = forms.DecimalField(max_digits=8, decimal_places=6, required=False)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=False)
    country = forms.ChoiceField(choices=[ (c.id, str(c)) for c in Country.objects.all() ], required=False)
    #platforms = forms.MultipleChoiceField(choices=[ (platform.id, str(platform)) for platform in Platform.objects.all() ])

    location = forms.CharField(max_length=255, required=False)

class AvatarForm(forms.Form):
    """
    The avatar form requires only one image field.
    """
    photo = forms.ImageField()
