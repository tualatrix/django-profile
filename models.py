# coding=UTF-8
from django.db import models
from django.contrib.sites.models import Site
from django.core.files.storage import Storage
from django.contrib.auth.models import User
#from django.contrib.gis.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
from django.template import loader, Context
from django.core.mail import send_mail
from django.conf import settings
from userprofile.countries import CountryField
import datetime
import cPickle as pickle
import base64
import Image, ImageFilter
import os.path

GENDER_CHOICES = ( ('F', _('Female')), ('M', _('Male')),)
GENDER_IMAGES = { "M": "%simages/male.png" % settings.MEDIA_URL, "F": "%simages/female.png" % settings.MEDIA_URL }
AVATAR_SIZES = (128, 96, 64, 48, 32, 24, 16)

class Profile(models.Model):
    """
    User profile model
    """

    firstname = models.CharField(max_length=255, blank=True)
    surname = models.CharField(max_length=255, blank=True)
    user = models.ForeignKey(User, unique=True)
    birthdate = models.DateField(default=datetime.date.today(), blank=True)
    date = models.DateTimeField(default=datetime.datetime.now)
    url = models.URLField(blank=True, core=True)
    about = models.TextField(blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    country = CountryField()
    location = models.CharField(max_length=255, blank=True)
    public = models.TextField(null=True)
    #point = models.PointField(blank=True, null=True)
    #objects = models.GeoManager()

    def avatar(self):
        try:
            return Avatar.objects.get(user=self.user, valid=True)
        except:
            return False

    def get_genderimage_url(self):
        return GENDER_IMAGES[self.gender]

    def __unicode__(self):
        return _("%s's profile") % self.user

    def get_genderimage_url(self):
        return GENDER_IMAGES[self.gender]

    def visible(self):
        try:
            return pickle.loads(base64.decodestring(self.public))
        except:
            return dict()

    def get_absolute_url(self):
        return "%sfor/%s/" % (settings.LOGIN_REDIRECT_URL, self.user)

    def yearsold(self):
        return (datetime.date.today().toordinal() - self.birthdate.toordinal()) / 365

    def save(self):
        if not self.public:
            public = dict()
            for item in self.__dict__.keys():
                public[item] = False
            public["user_id"] = True
            self.public = base64.encodestring(pickle.dumps(public, 2)).strip()
        super(Profile, self).save()


# TODO
class AvatarStorage(Storage):
    pass

class Avatar(models.Model):
    image = models.ImageField(upload_to="avatars/%Y/%b/%d")
    user = models.ForeignKey(User)
    date = models.DateTimeField(auto_now_add=True)
    valid = models.BooleanField()

    class Meta:
        unique_together = (('user', 'valid'),)

    def __unicode__(self):
        return _("%s's Avatar") % self.user

    def delete(self):
        base, filename = os.path.split(self.image.path)
        name, extension = os.path.splitext(filename)
        for key in AVATAR_SIZES:
            try:
                os.remove(os.path.join(base, "%s.%s%s" % (name, key, extension)))
            except:
                pass

        super(Avatar, self).delete()

class EmailValidationManager(models.Manager):

    def verify(self, key):
        try:
            verify = self.get(key=key)
            if not verify.is_expired():
                verify.user.email = verify.email
                verify.user.save()
                verify.delete()
                return True
            else:
                verify.delete()
                return False
        except:
            return False

    def getuser(self, key):
        try:
            return self.get(key=key).user
        except:
            return False

    def add(self, user, email):
        """
        Add a new validation process entry
        """
        while True:
            key = User.objects.make_random_password(70)
            try:
                EmailValidation.objects.get(key=key)
            except EmailValidation.DoesNotExist:
                self.key = key
                break

        template_body = "userprofile/email/validation.txt"
        template_subject = "userprofile/email/validation_subject.txt"
        site_name, domain = Site.objects.get_current().name, Site.objects.get_current().domain
        body = loader.get_template(template_body).render(Context(locals()))
        subject = loader.get_template(template_subject).render(Context(locals())).strip()
        send_mail(subject=subject, message=body, from_email=None, recipient_list=[email])
        user = User.objects.get(username=str(user))
        self.filter(user=user).delete()
        return self.create(user=user, key=key, email=email)

class EmailValidation(models.Model):
    user = models.ForeignKey(User, unique=True)
    email = models.EmailField(blank=True)
    key = models.CharField(max_length=70, unique=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    objects = EmailValidationManager()

    def __unicode__(self):
        return _("Email validation process for %(user)s") % { 'user': self.user }

    def is_expired(self):
        return (datetime.datetime.today() - self.created).days > 0

    def resend(self):
        """
        Resend validation email
        """
        template_body = "userprofile/email/validation.txt"
        template_subject = "userprofile/email/validation_subject.txt"
        site_name, domain = Site.objects.get_current().name, Site.objects.get_current().domain
        key = self.key
        body = loader.get_template(template_body).render(Context(locals()))
        subject = loader.get_template(template_subject).render(Context(locals())).strip()
        send_mail(subject=subject, message=body, from_email=None, recipient_list=[self.email])
        self.created = datetime.datetime.now()
        self.save()
        return True

