from django.conf import settings

from os.path import abspath, basename, dirname, join
import sys

directory = dirname(abspath(__file__))
PROJECT_ABSOLUTE_DIR = directory[:directory.rfind('/')]
PROJECT_NAME = basename(PROJECT_ABSOLUTE_DIR)

if hasattr(settings, 'LANGUAGE_CODE'):
    __import__(PROJECT_NAME + '.urls.' + settings.LANGUAGE_CODE,
               fromlist=['urlpatterns'])
else:
    from en import urlpatterns
