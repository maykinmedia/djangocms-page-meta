from collections import OrderedDict
from copy import deepcopy

from app_helper.base_test import BaseTestCase
from app_helper.utils import reload_urls
from django.conf import settings
from django.core.cache import cache
from django.test.client import RequestFactory


class DummyTokens(list):
    def __init__(self, *tokens):
        super().__init__(["dummy_tag"] + list(tokens))

    def split_contents(self):
        return self


class BaseTest(BaseTestCase):
    """
    Base class with utility function
    """

    page_data = {}
    _pages_data = (
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

    def setUp(self):
        super().setUp()
        cache.clear()

    def get_toolbar_request(self, page, user, path=None, edit=False, lang="en", use_middlewares=False, secure=False):
        """
        Changes CMS_TOOLBAR_URL__ENABLE to CMS_TOOLBAR_URL__ENABLE from parent function
        """

        from cms.utils.conf import get_cms_setting

        edit_on = get_cms_setting("CMS_TOOLBAR_URL__ENABLE")
        path = path or page and page.get_absolute_url(lang)
        if edit:
            path = "{}?{}".format(path, edit_on)

        request = RequestFactory().get(path, secure=secure)
        return self._prepare_request(request, page, user, lang, use_middlewares, use_toolbar=True, secure=secure)

    @staticmethod
    def create_pages(source, languages):
        """
        Removes all draft and publishing from parent function

        """
        from cms.api import create_page, create_title

        pages = OrderedDict()
        has_apphook = False
        home_set = False
        for page_data in source:
            main_data = deepcopy(page_data[languages[0]])

            main_data["language"] = languages[0]
            if main_data.get("parent", None):
                main_data["parent"] = pages[main_data["parent"]]
            page = create_page(**main_data)
            has_apphook = has_apphook or "apphook" in main_data
            for lang in languages[1:]:
                if lang in page_data:
                    title_data = deepcopy(page_data[lang])
                    title_data["language"] = lang
                    title_data["page"] = page
                    create_title(**title_data)
            if not home_set and hasattr(page, "set_as_homepage") and main_data.get("published", False):
                page.set_as_homepage()
                home_set = True
            pages[page.get_slug(languages[0])] = page
        if has_apphook:
            reload_urls(settings, cms_apps=True)
        return list(pages.values())
