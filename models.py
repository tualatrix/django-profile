from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
import datetime
import Image, ImageFilter
import os.path

AVATARSIZES = ( 128, 96, 64, 32, 16 )
GENDER_CHOICES = ( ('F', _('Female')), ('M', _('Male')),)

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


class Avatar(models.Model):
    """
    Avatar class. Every user can have one avatar associated.
    """
    photo = models.ImageField(upload_to="avatars/%Y/%b/%d")
    date = models.DateTimeField(default=datetime.datetime.now)
    user = models.OneToOneField(User, blank=True)
    box = models.CharField(max_length=255, blank=True)
    valid = models.BooleanField(default=False)

    def get_absolute_url(self):
        return "/site_media/%s" % self.photo

    def get_blur_url(self):
        return "%s.blur%s" % os.path.splitext(self.get_absolute_url())

    def __unicode__(self):
        return "%s-%s" % (self.user, self.photo)

    class Admin:
        pass

    def save(self):

        super(Avatar, self).save()

        if self.valid:
            Avatar.objects.filter(user=self.user).exclude(pk=self.pk).delete()
            base, ext = os.path.splitext(self.get_photo_filename())

            image = Image.open(self.get_photo_filename())
            box = self.box.split("-")
            box = [ int(num) for num in box ]
            image = image.crop(box)
            if image.mode not in ('L', 'RGB'):
                image = image.convert('RGB')

            for size in AVATARSIZES:
                image.thumbnail((size, size), Image.ANTIALIAS)
                image.save("%s.%s%s" % ( base, size, ext))

            del image

    def delete(self):
        filename = self.get_photo_filename()
        base, ext = os.path.splitext(filename)
        for size in AVATARSIZES:
            try:
                os.remove("%s.%s%s" % ( base, size, ext))
            except:
                pass

        try:
            os.remove(self.get_photo_filename())
        except:
            pass

        super(Avatar, self).delete()


class Profile(models.Model):
    """
    User profile model
    """

    firstname = models.CharField(max_length=255, blank=True)
    surname = models.CharField(max_length=255, blank=True)
    user = models.ForeignKey(User, unique=True, edit_inline=models.TABULAR,
                             num_in_admin=1,min_num_in_admin=1, max_num_in_admin=1,
                             num_extra_on_change=0)
    birthdate = models.DateField(default=datetime.date.today(), blank=True)
    date = models.DateTimeField(default=datetime.datetime.now)
    url = models.URLField(blank=True, core=True)
    about = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    country = models.ForeignKey(Country, null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)

    class Admin:
        pass

    def __unicode__(self):
        return _("%s's profile") % self.user

    def get_absolute_url(self):
        return "/profile/users/%s" % self.user

    def yearsold(self):
        return (datetime.date.today().toordinal() - self.birthdate.toordinal()) / 365
