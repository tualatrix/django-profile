# coding=UTF-8
from django.template import Library, Node, Template, TemplateSyntaxError, \
                            Variable
from django.utils.translation import ugettext as _
from userprofile.models import Avatar, AVATAR_SIZES, S3BackendNotFound
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
import urllib
from cStringIO import StringIO
from django.conf import settings
try:
    from PIL import Image
except ImportError:
    import Image

# from PythonMagick import Image
#from utils.TuxieMagick import Image
import os
import urlparse
import time
from django.core.files.storage import default_storage
if hasattr(settings, "AWS_SECRET_ACCESS_KEY"):
    try:
        from backends.S3Storage import S3Storage
        storage = S3Storage()
    except ImportError:
        raise S3BackendNotFound
else:
    storage = default_storage

register = Library()

if hasattr(settings, "DEFAULT_AVATAR") and settings.DEFAULT_AVATAR:
    DEFAULT_AVATAR = settings.DEFAULT_AVATAR
else:
    DEFAULT_AVATAR = os.path.join(settings.MEDIA_ROOT, "userprofile", "generic.jpg")

class ResizedThumbnailNode(Node):
    def __init__(self, size, username=None):
        try:
            self.size = int(size)
        except:
            self.size = Variable(size)

        if username:
            self.user = Variable(username)
        else:
            self.user = Variable("user")

    def render(self, context):
        # If size is not an int, then it's a Variable, so try to resolve it.
        if not isinstance(self.size, int):
            self.size = int(self.size.resolve(context))

        if not self.size in AVATAR_SIZES:
            return ''

        try:
            user = self.user.resolve(context)
            avatar = Avatar.objects.get(user=user, valid=True).image
            if hasattr(settings, "AWS_SECRET_ACCESS_KEY"):
                avatar_path = avatar.name
            else:
                avatar_path = avatar.path

            if not storage.exists(avatar_path):
                raise
            base, filename = os.path.split(avatar_path)
            name, extension = os.path.splitext(filename)
            filename = os.path.join(base, "%s.%s%s" % (name, self.size, extension))
            url_tuple = urlparse.urlparse(avatar.url)
            url = urlparse.urljoin(urllib.unquote(urlparse.urlunparse(url_tuple)), "%s.%s%s" % (name, self.size, extension))

            if not storage.exists(filename):
                thumb = Image.open(ContentFile(avatar.read()))
                thumb.thumbnail((self.size, self.size), Image.ANTIALIAS)
                f = StringIO()
                thumb.save(f, "JPEG")
                f.seek(0)
                storage.save(filename, ContentFile(f.read()))

        except:
            avatar_path = DEFAULT_AVATAR
            base, filename = os.path.split(avatar_path)
            generic, extension = os.path.splitext(filename)
            filename = os.path.join(base, "%s.%s%s" % (generic, self.size, extension))
            url = filename.replace(settings.MEDIA_ROOT, settings.MEDIA_URL)

        return url

@register.tag('avatar')
def Thumbnail(parser, token):
    bits = token.contents.split()
    username = None
    if len(bits) > 3:
        raise TemplateSyntaxError, _(u"You have to provide only the size as \
            an integer (both sides will be equal) and optionally, the \
            username.")
    elif len(bits) == 3:
        username = bits[2]
    elif len(bits) < 2:
        bits.append("96")
    return ResizedThumbnailNode(bits[1], username)
