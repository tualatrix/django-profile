from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
from django.contrib.sites.models import Site
from django.template import loader, Context
from django.core.mail import send_mail
from django.conf import settings
import datetime
import pickle
import Image, ImageFilter
import os.path

GENDER_CHOICES = ( ('F', _('Female')), ('M', _('Male')),)
GENDER_IMAGES = { "M": "%simages/male.png" % settings.MEDIA_URL, "F": "%simages/female.png" % settings.MEDIA_URL }

class Continent(models.Model):
    """
    Continent class. Simple class with the information about continents.
    It can be filled up with calling the "importdata" method:

    >>> Continent().importdata()

    """
    slug = models.SlugField(prepopulate_from=('name',), unique=True)
    code = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/continent/%s/" % self.slug

    class Admin:
        pass

    class Meta:
        verbose_name = _('Continent')
        verbose_name_plural = _('Continents')

class Country(models.Model):
    """
    Country class with the countries data needed in the Profile class. Dependent
    of the Continent class.
    To fill it with data, the file "countries.txt" is needed:
    >>> Country().importdata()
    """
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(prepopulate_from=('name',), unique=True)
    code = models.CharField(max_length=2, primary_key=True)
    continent = models.ForeignKey(Continent)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/country/%s/" % self.slug

    class Admin:
        list_display = ('name', 'continent')
        list_filter = ['continent']

    class Meta:
        ordering = ['name']
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')

class Profile(models.Model):
    """
    User profile model
    """

    firstname = models.CharField(max_length=255, blank=True)
    surname = models.CharField(max_length=255, blank=True)
    user = models.OneToOneField(User, primary_key=True)
    birthdate = models.DateField(default=datetime.date.today(), blank=True)
    date = models.DateTimeField(default=datetime.datetime.now)
    url = models.URLField(blank=True, core=True)
    about = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    country = models.ForeignKey(Country, null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    public = models.FileField(upload_to="avatars/%Y/%b/%d")

    # avatar
    avatar = models.ImageField(upload_to="avatars/%Y/%b/%d")
    avatartemp = models.ImageField(upload_to="avatars/%Y/%b/%d")
    avatar16 = models.ImageField(upload_to="avatars/%Y/%b/%d")
    avatar32 = models.ImageField(upload_to="avatars/%Y/%b/%d")
    avatar64 = models.ImageField(upload_to="avatars/%Y/%b/%d")
    avatar96 = models.ImageField(upload_to="avatars/%Y/%b/%d")

    class Admin:
        pass

    def __unicode__(self):
        return _("%s's profile") % self.user

    def get_genderimage_url(self):
        return GENDER_IMAGES[self.gender]

    def visible(self):
        try:
            return { 'user_id': True, 'avatar': True } + pickle.load(open(self.get_public_filename(), "rb"))
        except:
            return { 'user_id': True, 'avatar': True }

    def get_absolute_url(self):
        return "%s%s/" % (settings.LOGIN_REDIRECT_URL, self.user)

    def yearsold(self):
        return (datetime.date.today().toordinal() - self.birthdate.toordinal()) / 365

    def delete(self):
        for key in [ '', 'temp', '96', '64', '32', '16' ]:
            if getattr(self, "get_avatar%s_filename" % key)():
                try:
                    os.remove(getattr(self, "get_avatar%s_filename" % key)())
                except:
                    pass
        try:
            os.remove(self.public)
        except:
            pass 
        super(Profile, self).delete()

    def save(self):
        if not self.public:
            public = dict()
            for item in self.__dict__.keys():
                public[item] = False
            public["user_id"] = True
            public["avatar"] = True
            self.save_public_file("%s.public" % self.user, pickle.dumps(public))
        super(Profile, self).save()

class ValidationManager(models.Manager):

    def verify(self, key):
        try:
            verify = self.get(key=key)
            if not verify.is_expired():
                if verify.get_type_display() == "email":
                    verify.user.email = verify.email
                    verify.user.save()
                    verify.delete()
                elif verify.get_type_display() == "user":
                    verify.user.is_active = True
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

    def add(self, user, type, email):
        """
        Add a new validation process entry
        """
        while True:
            key = User.objects.make_random_password(70)
            try:
                Validation.objects.get(key=key)
            except Validation.DoesNotExist:
                self.key = key
                break

        site = Site.objects.get_current()
        template = "userprofile/%s_email.html" % type
        if type == "email":
            message = 'http://%s/accounts/email/change/%s/' % (site.domain, key)
            title = _("Email change confirmation on %s") % site.name
        elif type == "passwd":
            message = 'http://%s/accounts/password/change/%s/' % (site.domain, key)
            title = _("Password reset on %s") % site.name

        t = loader.get_template(template)
        site_name = site.name
        send_mail(title, t.render(Context(locals())), None, [email])
        user = User.objects.get(username=str(user))
        type_choices = { "email": 1, "passwd": 2, "user": 3}
        self.filter(user=user, type=type_choices[type]).delete()
        return self.create(user=user, key=key, type=type_choices[type], email=email)

class Validation(models.Model):
    type = models.PositiveSmallIntegerField(choices=( (1, 'email'), (2, 'passwd'),))
    user = models.ForeignKey(User)
    email = models.EmailField(blank=True)
    key = models.CharField(max_length=70, unique=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    objects = ValidationManager()

    class Meta:
        unique_together = ('type', 'user')

    class Admin:
        list_display = ('__unicode__',)
        search_fields = ('user__username', 'user__first_name')

    def __unicode__(self):
        return _("Email validation process for %(user)s of type %(type)s") % { 'user': self.user, 'type': self.get_type_display() }

    def is_expired(self):
        return (datetime.datetime.today() - self.created).days > 0

    def resend(self):
        """
        Resend validation email
        """
        site = Site.objects.get_current()
        type = self.get_type_display()
        template = "userprofile/%s_email.html" % type
        if type == "email":
            message = 'http://%s/accounts/email/change/%s/' % (site.domain, self.key)
            title = _("Email change confirmation on %s") % site.name
        elif type == "passwd":
            message = 'http://%s/accounts/password/change/%s/' % (site.domain, self.key)
            title = _("Password reset on %s") % site.name

        t = loader.get_template(template)
        site_name = site.name
        send_mail(title, t.render(Context(locals())), None, [self.email])
        self.created = datetime.datetime.now()
        self.save()
        return True

