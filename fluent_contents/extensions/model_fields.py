"""
This is an internal module for the plugin system,
the API is exposed via __init__.py

This package contains model fields which are usable for extensions.
"""
from django.conf import settings
from django.db import models
from fluent_contents.forms.widgets import WysiwygWidget


# Keep the apps optional, however, it's highly recommended to use them.
# This avoids fixing the generic plugin to specific extensions.
# Each project can use their preferred file browser/image browser/URL selector for the entire site.
if 'any_urlfield' in settings.INSTALLED_APPS:
    from any_urlfield.models import AnyUrlField
    PluginUrlField = AnyUrlField
else:
    PluginUrlField = models.URLField


if 'any_imagefield' in settings.INSTALLED_APPS:
    from any_imagefield.models import AnyFileField, AnyImageField
    PluginFileField = AnyFileField
    PluginImageField = AnyImageField
else:
    PluginFileField = models.FileField
    PluginImageField = models.ImageField


class HtmlField(models.TextField):
    """
    A large string field for HTML content; it's replaced with django-wysiwyg in the admin.
    """
    def formfield(self, **kwargs):
        defaults = {'widget': WysiwygWidget}
        defaults.update(kwargs)

        return super(HtmlField, self).formfield(**defaults)


# Tell South how to create custom fields
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], [
        "^fluent_contents\.extensions\.model_fields\.HtmlField",
    ])
except ImportError:
    pass

# Tell the Django admin it shouldn't override the widget because it's a TextField
from django.contrib.admin import options
options.FORMFIELD_FOR_DBFIELD_DEFAULTS[HtmlField] = {'widget': WysiwygWidget}
