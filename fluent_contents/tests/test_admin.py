from django.contrib.contenttypes.models import ContentType
from fluent_contents.models import Placeholder
from fluent_contents.tests.testapp.admin import PlaceholderFieldTestPageAdmin
from fluent_contents.tests.testapp.models import PlaceholderFieldTestPage, RawHtmlTestItem
from fluent_contents.tests.utils import AdminTestCase, override_settings


class AdminTest(AdminTestCase):
    """
    Test the admin functions.
    """
    model = PlaceholderFieldTestPage
    admin_class = PlaceholderFieldTestPageAdmin

    def setUp(self):
        self.settings = override_settings(
            MIDDLEWARE_CLASSES = (
                'django.middleware.common.CommonMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
            )
        )
        self.settings.enable()

    def tearDown(self):
        self.settings.disable()

    def test_add_page(self):
        """
        Test adding an object with placeholder field via the admin.
        """
        # Get all post data.
        # Includes all inlines, so all inline formsets of other plugins will be added (with TOTAL_FORMS 0)
        contents_slot = PlaceholderFieldTestPage.contents.slot
        formdata = {
            'title': 'TEST1',
            'placeholder-fs-TOTAL_FORMS': '1',
            'placeholder-fs-MAX_NUM_FORMS': '',   # Needed for Django <= 1.4.3
            'placeholder-fs-INITIAL_FORMS': '0',  # Needed for Django 1.3
            'placeholder-fs-0-slot': contents_slot,
            'placeholder-fs-0-role': Placeholder.MAIN,
            'contentitem-TOTAL_FORMS': '1',
            'contentitem-MAX_NUM_FORMS': '',
            'contentitem-INITIAL_FORMS': '0',
            'contentitem-0-polymorphic_ctype': ContentType.objects.get_for_model(RawHtmlTestItem).pk,
            'contentitem-0-placeholder': '',                   # The placeholder is not defined yet, as item is not yet created.
            'contentitem-0-placeholder_slot': contents_slot,   # BaseContentItemFormSet resolves the placeholder after it's created
            'contentitem-0-sort_order': '1',
            'contentitem-0-html': u'<b>foo</b>',
        }

        # Make a POST to the admin page.
        self.admin_post_add(formdata)

        # Check that the page exists.
        page = PlaceholderFieldTestPage.objects.get(title='TEST1')

        # Check that the placeholder is created,
        # and properly links back to it's parent.
        placeholder = page.contents
        self.assertEqual(placeholder.slot, contents_slot)
        self.assertEqual(placeholder.role, Placeholder.MAIN)
        self.assertEqual(placeholder.parent, page)

        # Check that the ContentItem is created,
        # and properly links back to it's parent.
        rawhtmltestitem = RawHtmlTestItem.objects.get(html=u'<b>foo</b>')
        self.assertEqual(rawhtmltestitem.placeholder, placeholder)
        self.assertEqual(rawhtmltestitem.parent, page)

        # Also check reverse relation of placeholder
        rawhtmltestitem = placeholder.contentitems.all()[0]
        self.assertEqual(rawhtmltestitem.html, u'<b>foo</b>')


def _get_url_format(opts):
    try:
        return opts.app_label, opts.model_name  # Django 1.7 format
    except AttributeError:
        return opts.app_label, opts.module_name
