# coding=UTF-8
from django.template import Library, Node, Template, TemplateSyntaxError, \
                            Variable
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as u_
from django.contrib.auth.models import User
from django.conf import settings

from userprofile import profile_settings as _settings
from userprofile.models import Profile
# from PythonMagick import Image
from utils.TuxieMagick import Image

from os import path, makedirs
from shutil import copy

register = Library()

class ResizedThumbnailNode(Node):
    def __init__(self, size, username=None):
        try:
            self.size = int(size)
        except:
            self.size = Variable(size)
        self.user = username

    def render(self, context):
        # If size is not an int, then it's a Variable, so try to resolve it.
        # If there's a username, go get it! Otherwise get the current.
        try:
            if not isinstance(self.size, int):
                self.size = int(self.size.resolve(context))
            if self.user:
                try:
                    self.user = User.objects.get(username=self.user)
                except:
                    self.user = Variable(self.user).resolve(context)
            else:
                self.user = Variable('user').resolve(context)
        except Exception, e:
            print e
            return '' # just die...
        size_equals = self.size == _settings.DEFAULT_AVATAR_WIDTH
        if self.size > _settings.DEFAULT_AVATAR_WIDTH:
            return '' # unacceptable
        # Maybe django-profile it's not set as AUTH_PROFILE_MODULE
        try:
            profile = self.user.get_profile()
        except Exception, e:
            print e
            profile = Profile.objects.get(user=self.user)
        # For compatibility with the official django-profile model I check
        # whether it's a path or just a filename.
        # In my opinion in the database should only be saved the file name,
        # and all files be stored in a standard directory:
        # settings.AVATAR_DIRS[int]/str(User)/settings_DEFAULT_AVATAR_WIDTH/
        try:
            filename = profile.avatar[profile.avatar.rindex('/')+1:]
        except:
            if profile.avatar:
                filename = profile.avatar
            else:
                filename = _settings.DEFAULT_AVATAR
        # Avatar's heaven, where all the avatars go.
        avatars_root = path.join(_settings.AVATARS_DIR,
                                 slugify(self.user.username))
        file_root = path.join(avatars_root, str(self.size))
        if not path.exists(file_root):
            makedirs(file_root)
        file_path = '%(root)s/%(file)s' % {'root': file_root, 'file': filename}
        print 'file_path:', file_path
        # I can't return an absolute path... can I?
        file_url = file_path.replace(settings.MEDIA_ROOT, settings.MEDIA_URL)
        if path.exists(file_path):
            return file_url
        # Oops, I din't find it, let's try to generate it.
        orig_root = path.join(avatars_root, 
                              str(_settings.DEFAULT_AVATAR_WIDTH))
        # The OS path to the image file.
        orig_path = path.join(orig_root, str(_settings.DEFAULT_AVATAR_WIDTH),
                              filename)
        # Look for the original avatar in the standard directory, if found,
        # save the location for later use.
        if not path.exists(orig_path):
            try:
                makedirs(orig_root)
            except Exception, e:
                print e
                # Nothing was found... let's try something else.
                pass
            # For compatibility with the official model, I check if the old
            # path exists. If it does, I copy it to the new standard location.
            if profile.avatar:
                orig_path = path.join(settings.MEDIA_ROOT, profile.avatar)
                if path.exists(orig_path):
                    orig_file = Image(orig_path)
                    print orig_path
                    dest_root = path.join(avatars_root,
                                          str(orig_file.size().width()))
                    try:
                        makedirs(dest_root)
                        copy(orig_path, dest_root)
                    except Exception, e:
                        print e
                        return ''
                    # I save the new orig_path for later.
                    orig_path = path.join(dest_root, filename)
                # Did my best...
                else:
                    return '' # fail silently
            else:
                return path.join(
                    _settings.AVATARS_DIR, _settings.DEFAULT_AVATAR).replace(
                        settings.MEDIA_ROOT, settings.MEDIA_URL)
        else:
            # I found it, and was already scaled! Great news.
            if size_equals:
                return orig_path.replace(settings.MEDIA_ROOT, \
                                          settings.MEDIA_URL)
        orig_file = Image(orig_path)
        orig_file.scale(self.size)
        # file_path, what we were looking for in the first place... remember?
        if orig_file.write(file_path):
            return file_url
        else:
            print '=== ERROR ==='
            return '' # damn! Close but no cigar...

def Thumbnail(parser, token):
    bits = token.contents.split()
    username = None
    if len(bits) > 3:
        raise TemplateSyntaxError, u_(u"You have to provide only the size as \
            an integer (both sides will be equal) and optionally, the \
            username.")
    elif len(bits) == 3:
        username = bits[2]
    elif len(bits) < 2:
        bits.append(_settings.DEFAULT_AVATAR_WIDTH)
    return ResizedThumbnailNode(bits[1], username)

register.tag('avatar', Thumbnail)
