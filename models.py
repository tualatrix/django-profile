from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
from django.conf import settings
import datetime
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

    def importdata(self):
        Continent.objects.all().delete()
        Continent(name="Asia", slug=slugify("Asia"), code="AS").save()
        Continent(name="Africa", slug=slugify("Africa"), code="AF").save()
        Continent(name="Europe", slug=slugify("Europe"), code="EU").save()
        Continent(name="North America", slug=slugify("North America"), code="NA").save()
        Continent(name="South America", slug=slugify("South America"), code="SA").save()
        Continent(name="Oceania", slug=slugify("Oceania"), code="OC").save()
        Continent(name="Antarctica", slug=slugify("Antarctica"), code="AN").save()

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

    def importdata(self, file="db/countries.txt"):
        Country.objects.all().delete()
        f = open(file)
        for line in f.xreadlines():
            line = line.strip()
            d, name = line.split('"')[:-1]
            continent, code = d.split(",")[:-1]
            c = Continent.objects.filter(code=continent)[0]
            p = Country(name=name, slug=slugify(name), code=code, continent=c)
            p.save()

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
    latitude = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    country = models.ForeignKey(Country, null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)

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

    def get_absolute_url(self):
        return "/profile/users/%s/" % self.user

    def yearsold(self):
        return (datetime.date.today().toordinal() - self.birthdate.toordinal()) / 365

    def delete(self):
        os.remove(self.get_avatar_filename())
        super(Profile, self).delete()
