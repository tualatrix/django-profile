from django.contrib.sites.models import Site
from django.conf import settings
import types

def site(request):
    """
    Adds site-related context variables to the context.
    """
    current_site = Site.objects.get_current()

    return {
        'SITE_NAME': current_site.name,
        'SITE_DOMAIN': current_site.domain,
        'SITE_URL': "http://www.%s" % (current_site.domain),
    }

# see "css_classes" below 
CSS_CLASSES = {
    # for "blueprint css", full width
    'blueprint': {
        'content_main_2col':    'span-13 prepend-1 colborder',
        'content_related':      'span-8 last',
        'content_main':         'span-22 prepend-1 append-1',
        'nav':                  'span-24 last',
        'public_vcard_content': 'span-10',
        'public_vcard_map':     'span-10',
        'overview_avatar':      'span-3',
        'overview_details':     'span-9 last',
        'overview_location':    'span-12 last',
    },
    # for "960gs" with 12 columns, full width
    '960gs-12': {
        'content_main_2col':    'grid_8 alpha',
        'content_related':      'grid_4 omega',
        'content_main':         'grid_12 alpha omega',
        'nav':                  'grid_12 alpha omega',
        'public_vcard_content': 'grid_6 alpha',
        'public_vcard_map':     'grid_6 omega',
        'overview_avatar':      'grid_2 alpha',
        'overview_details':     'grid_6 omega',
        'overview_location':    'grid_8 alpha omega',
    },
    # for "960gs" with 16 columns, full width
    '960gs-16': {
        'content_main_2col':    'grid_12 alpha',
        'content_related':      'grid_4 omega',
        'content_main':         'grid_16 alpha omega',
        'nav':                  'grid_16 alpha omega',
        'public_vcard_content': 'grid_8 alpha',
        'public_vcard_map':     'grid_8 omega',
        'overview_avatar':      'grid_3 alpha',
        'overview_details':     'grid_9 omega',
        'overview_location':    'grid_12 alpha omega',
    },
    # for "960gs" with 12 columns, inside a width of 9 columns (as example)
    '960gs-12-in-9': {
        'content_main_2col':    'grid_6 alpha omega',
        'content_related':      'grid_3 omega',
        'content_main':         'grid_9 alpha',
        'nav':                  'grid_9 alpha omega',
        'public_vcard_content': 'grid_4 alpha',
        'public_vcard_map':     'grid_5 omega',
        'overview_avatar':      'grid_2 alpha',
        'overview_details':     'grid_6 omega',
        'overview_location':    'grid_6 alpha omega',
    },
}

def css_classes(request):
    """
    If USERPROFILE_CSS_CLASSES  is in the settings, it should be a string
    (a key for the above dict "CSS_CLASSES", or a dict, with the same
    keys as "CSS_CLASSE"
    In templates, you should use 
        class="{{css_classes.key}}"
    with key one of keys described above.
    """
    try:
        if isinstance(settings.USERPROFILE_CSS_CLASSES, types.StringTypes) \
            and settings.USERPROFILE_CSS_CLASSES in CSS_CLASSES:
            css_dict = CSS_CLASSES[settings.USERPROFILE_CSS_CLASSES]
        else:
            css_dict = settings.USERPROFILE_CSS_CLASSES
    except:
        css_dict = CSS_CLASSES['blueprint']

    return { 'css_classes': css_dict }
