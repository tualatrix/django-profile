from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from forms import ProfileForm, AvatarForm
from models import Profile
from django.core.exceptions import ObjectDoesNotExist
from django.utils import simplejson
from django.contrib.auth.models import User
from profile.models import Avatar, Profile
from account.models import EmailValidate
import random
import Image, ImageFilter

def public(request, user, template):
    cuser = User.objects.get(username=user)
    try:
        profile = Profile.objects.get(user=cuser)
        avatar = Avatar.objects.get(user=cuser, valid=True)
    except:
        pass
    user = request.user

    return render_to_response(template, locals())

@login_required
def private(request, APIKEY, template):
    """
    Private part of the user profile
    """
    apikey = APIKEY
    user = request.user
    try:
        email = EmailValidate.objects.get(user=str(user)).email
        validated = False
    except:
        email = User.objects.get(username=str(user)).email
        validated = True
    form = ProfileForm(request)

    try:
        avatar = Avatar.objects.filter(user=user, valid=True)[0]
    except:
        pass

    if request.method == "POST" and form.is_valid():
        form.save()

    profile = Profile.objects.get(user=user)
    lat = profile.latitude
    lng = profile.longitude

    return render_to_response(template, locals())

@login_required
def delete(request, template):
    user = str(request.user)
    if request.method == "POST":
        # Remove the profile
        Profile.objects.get(user=user).delete()
        # Remove the avatar if exists
        try:
            Avatar.objects.get(user=user).delete()
        except:
            pass
        # Remove the e-mail of the account too
        acct = User.objects.get(username=user)
        acct.email = ''
        acct.save()

        return HttpResponseRedirect('%sdone/' % request.path)

    return render_to_response(template, locals())

@login_required
def avatar(request, template, step="one"):
    """
    Avatar management
    """
    if not request.method == "POST":
        form = AvatarForm()
    else:
        if step=="one":
            form = AvatarForm(request.POST, request.FILES)
            if form.is_valid():
                data = form.cleaned_data
                Avatar.objects.filter(user=request.user, valid=False).delete()
                avatar = Avatar(user=request.user)
                avatar.save_photo_file(data['photo'].filename, data['photo'].content)
                avatar.save()
                im = Image.open(avatar.get_photo_filename())

                # Resize if needed
                width = avatar.get_photo_width()
                height= avatar.get_photo_height()
                if width > height and width > 640:
                    im = im.resize((640, 640*height/width), Image.ANTIALIAS)
                    im.save(avatar.get_photo_filename())
                    width, height = im.size
                elif height > 480:
                    im = im.resize((480*width/height, 480), Image.ANTIALIAS)
                    im.save(avatar.get_photo_filename())
                    width, height = im.size

                if width < 96 or height < 96:
                    cropsize = 32
                else:
                    cropsize = 96

                cx = width/2 - 48
                if cx < 0: cx=0
                cy = height/2 - 48
                if cy < 0: cy=0

                # Generate blur and scale image
                blur = im.filter(ImageFilter.BLUR)
                blur = blur.convert("L")
                blur.save("%s_blur.jpg" % avatar.get_photo_filename())
                blur_url = "%s_blur.jpg" % avatar.get_absolute_url()


        elif step=="two":
                avatar = Avatar.objects.get(user = request.user, pk = request.POST.get('avatar_id'))
                avatar.valid = True
                avatar.save()
                im = Image.open(avatar.get_photo_filename())
                if request.POST.get('top') and request.POST.get('left') and request.POST.get('size'):
                    top = request.POST.get('top')
                    left = request.POST.get('left')
                    size = request.POST.get('size')
                    box = ( int(left), int(top), int(left) + int(size), int(top) + int(size))
                    im = im.crop(box)
                resized = im.resize((96, 96), Image.ANTIALIAS)
                resized.save(avatar.get_photo_filename())
                done = True

    return render_to_response(template, locals())

@login_required
def avatarDelete(request, avatar_id=False):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and not avatar_id:
        Avatar.objects.filter(user=request.user).delete()
        return HttpResponse(simplejson.dumps({'success': True}))
    elif avatar_id:
        Avatar.objects.filter(user=request.user, pk=avatar_id).delete()
        return HttpResponse(simplejson.dumps({'success': True}))
    else:
        return HttpResponseRedirect("/")
