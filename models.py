from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
import datetime
import os.path

class Continent(models.Model):
    """
    Continent class. Simple class with the information about continents.
    It can be filled up with calling the "importdata" method:

    >>> Continent().importdata()

    """
    slug = models.SlugField(prepopulate_from=('name',), unique=True)
    code = models.CharField(maxlength=2, primary_key=True)
    name = models.CharField(maxlength=255, unique=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/continent/%i/" % self.id

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
    To fill it with data, he needes the file "countries.txt":
    >>> Country().importdata()
    """
    name = models.CharField(maxlength=255, unique=True)
    slug = models.SlugField(prepopulate_from=('name',), unique=True)
    code = models.CharField(maxlength=2, primary_key=True)
    continent = models.ForeignKey(Continent)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/country/%i/" % self.id

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
    user = models.OneToOneField(User, blank=True, null=True)
    valid = models.BooleanField(default=False)

    def get_absolute_url(self):
        return "/site_media/%s" % self.photo

    def __unicode__(self):
        return "%s-%s" % (self.user, self.photo)

    class Admin:
        pass

class Profile(models.Model):
    """
    User profile model
    """

    GENDER_CHOICES = ( ('F', _('Female')), ('M', _('Male')),)

    firstname = models.CharField(maxlength=255, blank=True)
    surname = models.CharField(maxlength=255, blank=True)
    user = models.ForeignKey(User, unique=True, edit_inline=models.TABULAR,
                             num_in_admin=1,min_num_in_admin=1, max_num_in_admin=1,
                             num_extra_on_change=0)
    birthdate = models.DateTimeField(default=datetime.datetime.now(), blank=True)
    url = models.URLField(blank=True, core=True)
    about = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=8, decimal_places=6, default=-100)
    longitude = models.DecimalField(max_digits=8, decimal_places=6, default=-100)
    gender = models.CharField(maxlength=1, choices=GENDER_CHOICES, blank=True)
    country = models.ForeignKey(Country, blank=True, null=True)
    location = models.CharField(maxlength=255, blank=True)

    class Admin:
        pass

    def __unicode__(self):
        return "%s" % self.user

    def yearsold(self):
        return (datetime.datetime.now().toordinal() - self.birthdate.toordinal()) / 365

    def htmlprint(self):
        gender = { "M": "/site_media/images/male.png", "F": "/site_media/images/female.png" }
        try:
            if Avatar.objects.get(user=self.user).get_photo_filename() and os.path.isfile(Avatar.objects.get(user=self.user).get_photo_filename()):
                avatar_url = Avatar.objects.get(user=self.user).get_absolute_url()
            else:
                raise Exception()
        except:
            avatar_url = "/site_media/images/default.gif"

        return """
<div class="vcard">
<img class="photo" src="%s" alt="%s"/>
<ul style="float: left;">
  <li class="fn nickname">%s</li>
  %s
  %s
  %s
  %s
</ul>
</div>
""" % (avatar_url, self.user, self.user, self.country and "<li>%s</li>" % self.country or 'No country', self.birthdate.year < datetime.datetime.now().year and _("%s years old") % self.yearsold() or '', self.url and "<li><a class=\"url\" href=\"%s\">%s</a></li>" % ( self.url, _("My Blog")), self.gender and "<li style=\"margin: 10px 0px 0px 110px;\"><img src=\"%s\"></li>" % gender.get(self.gender) or '',)
