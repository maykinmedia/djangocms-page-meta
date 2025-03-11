from collections import OrderedDict
from copy import deepcopy

from app_helper.base_test import CreateTestDataMixin
from cms.api import create_page, create_page_content
from cms.models import PageContent
from cms.test_utils.testcases import CMSTestCase
from django.contrib.auth.models import Permission
from django.core.cache import cache


class DummyTokens(list):
    def __init__(self, *tokens):
        super().__init__(["dummy_tag"] + list(tokens))

    def split_contents(self):
        return self


class BaseTest(CMSTestCase):
    """
    Base class with utility function
    """

    language = "en"
    languages = ["en", "fr-fr", "it"]

    pages_data = (
        {
            "en": {"title": "page one", "template": "page_meta.html"},
            "fr-fr": {"title": "page un"},
            "it": {"title": "pagina uno"},
        },
        {
            "en": {"title": "page two", "template": "page_meta.html"},
            "fr-fr": {"title": "page deux"},
            "it": {"title": "pagina due"},
        },
    )

    title_data = {
        "keywords": "keyword1, keyword2, keyword3",
        "description": "base lorem ipsum - english",
        "og_description": "opengraph - lorem ipsum - english",
        "twitter_description": "twitter - lorem ipsum - english",
        "schemaorg_description": "gplus - lorem ipsum - english",
    }
    title_data_it = {
        "keywords": "parola1, parola2, parola3",
        "description": "base lorem ipsum - italian",
        "og_description": "opengraph - lorem ipsum - italian",
        "twitter_description": "twitter - lorem ipsum - italian",
        "schemaorg_description": "gplus - lorem ipsum - italian",
    }
    og_data = {
        "og_type": "article",
        "og_author_url": "https://facebook.com/FakeUser",
        "og_author_fbid": "123456789",
        "og_publisher": "https://facebook.com/FakeUser",
        "og_app_id": "123456789",
        "fb_pages": "PAGES123456789",
    }
    twitter_data = {
        "twitter_author": "fake_user",
        "twitter_site": "fake_site",
        "twitter_type": "summary",
    }
    robots_data_single = {"robots": "['noindex']"}
    robots_data_multiple = {"robots": "['none', 'noimageindex', 'noarchive']"}

    image_name = "test_image.jpg"

    def setUp(self):
        super().setUp()
        assert self.language == self.languages[0]

        self.superuser = self.get_superuser()
        self.staff_user = self.get_staff_user_with_std_permissions()

        cache.clear()

    def create_pages(self):
        """
        Removes all draft and publishing from parent function

        """
        home_set = False
        pages = OrderedDict()

        for page_data in self.pages_data:

            main_data = deepcopy(page_data[self.language])
            main_data["language"] = self.language
            main_data["created_by"] = self.superuser
            page = create_page(**main_data)

            for lang in self.languages[1:]:
                context_data = deepcopy(page_data[lang])
                context_data["language"] = lang
                context_data["page"] = page
                context_data["created_by"] = self.superuser
                create_page_content(**context_data)

            if not home_set:
                page.set_as_homepage()
                home_set = True
            pages[page.get_slug(self.language)] = page

        return list(pages.values())

    def _add_default_permissions(self, user):
        # Page permissions
        user.user_permissions.add(Permission.objects.get(codename="publish_page"))
        user.user_permissions.add(Permission.objects.get(codename="add_page"))
        user.user_permissions.add(Permission.objects.get(codename="change_page"))
        user.user_permissions.add(Permission.objects.get(codename="delete_page"))

    create_filer_image = CreateTestDataMixin.create_filer_image
    create_django_image = CreateTestDataMixin.create_django_image

    def create_filer_image_object(self):
        self.filer_image = self.create_filer_image(self.staff_user, self.image_name)
        return self.filer_image

    def publish_page(self, page, language):
        content = PageContent.admin_manager.get(page=page, language=language)
        version = content.versions.first()
        version.publish(self.superuser)
