from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
import datetime
import os.path

class Continent(models.Model):
    """
    Continent class
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
    Country class
    """
    name = models.CharField(maxlength=255, unique=True)
    slug = models.SlugField(prepopulate_from=('name',), unique=True)
    code = models.CharField(maxlength=2, primary_key=True)
    continent = models.ForeignKey(Continent)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/country/%i/" % self.id

    def importdata(self, file="../countries.txt"):
        Country.objects.all().delete()
        f = open(file)
        for line in f.xreadlines():
            line = line.strip()
            print line
            d, name = line.split('"')[:-1]
            continent, code = d.split(",")[:-1]
            print continent, code, name
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
    blog = models.URLField(blank=True, core=True)
    about = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=8, decimal_places=6, default=40.416706)
    longitude = models.DecimalField(max_digits=8, decimal_places=6, default=-3.703269)
    gender = models.CharField(maxlength=1, choices=GENDER_CHOICES, blank=True)
    country = models.ForeignKey(Country, blank=True, null=True)
    city = models.CharField(maxlength=255, blank=True)

    class Admin:
        pass

    def __unicode__(self):
        return "%s" % self.user

    def htmlprint(self):
        try:
            if Avatar.objects.get(user=self.user).get_photo_filename() and os.path.isfile(Avatar.objects.get(user=self.user).get_photo_filename()):
                avatar_url = Avatar.objects.get(user=self.user).get_absolute_url()
            else:
                raise Exception()
        except:
            avatar_url = "/site_media/images/default.gif"

        return """
<div class="usercard">
<img style="float: left;" src="%s" />
<ul style="float: left;">
  <li style="font-weight: bold;">%s</li>
  %s
  %s
  %s
</ul>
</div>
""" % (avatar_url, self.user, self.country and "<li>%s</li>" % self.country or 'No country', self.gender and "<li>%s</li>" % self.gender, self.blog and "<li><a href=\"%s\">Blog</a></li>" % self.blog)
