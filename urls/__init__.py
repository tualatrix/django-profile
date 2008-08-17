from django.conf import settings
from os.path import abspath, basename, dirname, join

directory = dirname(abspath(__file__))
PROJECT_ABSOLUTE_DIR = directory[:directory.rfind('/')]
PROJECT_NAME = basename(PROJECT_ABSOLUTE_DIR)

if hasattr(settings, "I18N_URLS") and settings.I18N_URLS:
    try:
        module = __import__("%s.urls.%s" % (PROJECT_NAME, \
                            settings.LANGUAGE_CODE), {}, {}, "urlpatterns")
        globals().update({ "urlpatterns": module.__dict__["urlpatterns"] })
    except:
        module = __import__("%s.urls.en" % (PROJECT_NAME), {}, {}, "urlpatterns")
        globals().update({ "urlpatterns": module.__dict__["urlpatterns"] })
else:
    module = __import__("%s.urls.en" % (PROJECT_NAME), {}, {}, "urlpatterns")
    globals().update({ "urlpatterns": module.__dict__["urlpatterns"] })
