from django import forms
from django.core.exceptions import ObjectDoesNotExist
from userprofile.models import Profile, GENDER_CHOICES
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from userprofile.models import Country, Validation
from django.core.files.uploadedfile import SimpleUploadedFile
import mimetypes, urllib

class LocationForm(forms.ModelForm):
    """
    Profile Form. Composed by all the Profile model fields.
    """

    class Meta:
        model = Profile
        fields = ('location', 'latitude', 'longitude', 'country')

class ProfileForm(forms.ModelForm):
    """
    Profile Form. Composed by all the Profile model fields.
    """
    class Meta:
        model = Profile
        fields = ('firstname', 'surname', 'birthdate', 'gender', 'url', 'about')

class AvatarForm(forms.Form):
    """
    The avatar form requires only one image field.
    """
    photo = forms.ImageField(required=False)
    url = forms.URLField(required=False)

    def clean_url(self):
        url = self.cleaned_data.get('url')
        if not url: return ''
        filename, headers = urllib.urlretrieve(url)
        if not mimetypes.guess_all_extensions(headers.get('Content-Type')):
            raise forms.ValidationError(_('The file type is invalid: %s' % type))
        return SimpleUploadedFile(filename, open(filename).read(), content_type=headers.get('Content-Type'))

    def clean(self):
        if not (self.cleaned_data.get('photo') or self.cleaned_data.get('url')):
            raise forms.ValidationError(_('You must enter one of the options'))
        return self.cleaned_data

class AvatarCropForm(forms.Form):
    """
    Crop dimensions form
    """
    top = forms.IntegerField()
    bottom = forms.IntegerField()
    left = forms.IntegerField()
    right = forms.IntegerField()

    def clean(self):
        if int(self.cleaned_data.get('right')) - int(self.cleaned_data.get('left')) < 96:
            raise forms.ValidationError(_("You must select a portion of the image with a minimum of 96x96 pixels."))
        else:
            return self.cleaned_data

class RegistrationForm(forms.Form):

    username = forms.CharField(max_length=255, min_length = 3, label=_("Username"))
    email = forms.EmailField(required=False, label=_("E-mail address"))
    password1 = forms.CharField(min_length=6, widget=forms.PasswordInput(render_value=False), label=_("Password"))
    password2 = forms.CharField(min_length=6, widget=forms.PasswordInput(render_value=False), label=_("Password (again)"))

    def clean_username(self):
        """
        Verify that the username isn't already registered
        """
        username = self.cleaned_data.get("username")
        if not set(username).issubset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"):
            raise forms.ValidationError(_("That username has invalid characters. The valid values are letters, numbers and underscore."))

        if User.objects.filter(username__iexact=username).count() == 0:
            return username
        else:
            raise forms.ValidationError(_("The username is already registered."))

    def clean(self):
        """
        Verify that the 2 passwords fields are equal
        """
        if self.cleaned_data.get("password1") == self.cleaned_data.get("password2"):
            return self.cleaned_data
        else:
            raise forms.ValidationError(_("The passwords inserted are different."))

    def clean_email(self):
        """
        Verify that the email exists
        """
        email = self.cleaned_data.get("email")

        if not email: return  email

        try:
            User.objects.get(email=email)
            raise forms.ValidationError(_("That e-mail is already used."))
        except User.DoesNotExist:
            try:
                Validation.objects.get(email=email)
                raise forms.ValidationError(_("That e-mail is already being confirmed."))
            except Validation.DoesNotExist:
                return email

class EmailValidationForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        """
        Verify that the email exists
        """
        email = self.cleaned_data.get("email")
        if not (User.objects.filter(email=email) or Validation.objects.filter(email=email)):
            return email

        raise forms.ValidationError(_("That e-mail is already used."))

class ValidationForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        """
        Verify that the email or the user exists
        """
        email = self.cleaned_data.get("email")
        try:
            User.objects.get(email=email)
        except:
            raise forms.ValidationError(_("There's no user with that e-mail"))

        return email

class changePasswordKeyForm(forms.Form):
    newpass1 = forms.CharField(min_length=6, widget=forms.PasswordInput)
    newpass2 = forms.CharField(min_length=6, widget=forms.PasswordInput)

    def clean(self):
        """
        Verify the equality of the two passwords
        """

        if self.cleaned_data.get("newpass1") and self.cleaned_data.get("newpass1") == self.cleaned_data.get("newpass2"):
            return self.cleaned_data
        else:
            raise forms.ValidationError(_("The passwords inserted are different."))

    def save(self, key):
        "Saves the new password."
        lostpassword = Validation.objects.get(key=key)
        user = lostpassword.user
        user.set_password(self.cleaned_data.get('newpass1'))
        user.save()
        lostpassword.delete()

class changePasswordAuthForm(forms.Form):
    newpass1 = forms.CharField( min_length = 6, widget = forms.PasswordInput )
    newpass2 = forms.CharField( min_length = 6, widget = forms.PasswordInput )

    def clean(self):
        """
        Verify the equality of the two passwords
        """

        if self.cleaned_data.get("newpass1") and self.cleaned_data.get("newpass1") == self.cleaned_data.get("newpass2"):
            return self.cleaned_data
        else:
            raise forms.ValidationError(_("The passwords inserted are different."))

    def save(self, user):
        "Saves the new password."
        user.set_password(self.cleaned_data.get('newpass1'))
        user.save()
