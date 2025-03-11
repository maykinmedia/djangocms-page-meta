from cms.models import PageContent

from djangocms_page_meta.models import GenericMetaAttribute, PageMeta, TitleMeta

from .base import BaseTest


class TemplateMetaTest(BaseTest):
    def test_page_meta(self):
        """
        Test page-level templatetags
        """
        page1 = self.create_pages()[0]
        page_ext = PageMeta.objects.create(extended_object=page1)
        for key, val in self.og_data.items():
            setattr(page_ext, key, val)
        page_ext.save()

        GenericMetaAttribute.objects.create(page=page_ext, attribute="custom", name="attr", value="foo")
        # page1.publication_end_date = page1.publication_date + timedelta(days=1)
        page1.save()
        self.publish_page(page1, "it")
        self.publish_page(page1, "en")

        response = self.client.get(page1.get_absolute_url("en"))
        self.assertContains(response, '<meta name="twitter:domain" content="example.com">')
        # self.assertContains(
        #     response, '<meta itemprop="datePublished" content="%s">' % page1.publication_date.isoformat()
        # )
        # self.assertContains(
        #     response, '<meta property="article:expiration_time" content="%s">' % page1.publication_end_date.isoformat()
        # )
        self.assertContains(response, '<meta property="article:publisher" content="https://facebook.com/FakeUser">')
        self.assertContains(response, '<meta custom="attr" content="foo">')

    def test_page_meta_robots_no_data(self):
        """
        Test page-level no robots templatetags
        """
        page1 = self.create_pages()[0]
        page_ext = PageMeta.objects.create(extended_object=page1)
        page_ext.save()
        page1.save()
        self.publish_page(page1, "en")
        response = self.client.get(page1.get_absolute_url("en"))
        self.assertNotContains(response, '<meta name="robots"')

    def test_page_meta_robots_single(self):
        """
        Test page-level robots single templatetags
        """
        page1 = self.create_pages()[0]
        page_ext = PageMeta.objects.create(extended_object=page1)
        for key, val in self.robots_data_single.items():
            setattr(page_ext, key, val)
        page_ext.save()
        page1.save()
        self.publish_page(page1, "en")
        response = self.client.get(page1.get_absolute_url("en"))
        self.assertContains(response, '<meta name="robots" content="noindex">')

    def test_page_meta_robots_multiple(self):
        """
        Test page-level robots multiple templatetags
        """
        page1 = self.create_pages()[0]
        page_ext = PageMeta.objects.create(extended_object=page1)
        for key, val in self.robots_data_multiple.items():
            setattr(page_ext, key, val)
        page_ext.save()
        page1.save()
        self.publish_page(page1, "en")
        response = self.client.get(page1.get_absolute_url("en"))
        self.assertContains(response, '<meta name="robots" content="none, noimageindex, noarchive">')

    def test_title_meta(self):
        """
        Test title-level templatetags
        """
        page1 = self.create_pages()[0]
        content_en = PageContent.admin_manager.get(page=page1, language="en")
        content_it = PageContent.admin_manager.get(page=page1, language="it")
        title_ext = TitleMeta.objects.create(extended_object=content_en)
        for key, val in self.title_data.items():
            setattr(title_ext, key, val)
        title_ext.save()
        GenericMetaAttribute.objects.create(title=title_ext, attribute="custom", name="attr", value="foo-en")
        title_ext = TitleMeta.objects.create(extended_object=content_it)
        for key, val in self.title_data_it.items():
            setattr(title_ext, key, val)
        title_ext.save()
        GenericMetaAttribute.objects.create(title=title_ext, attribute="custom", name="attr", value="foo-it")
        self.publish_page(page1, "it")
        self.publish_page(page1, "en")

        # Italian language
        response = self.client.get(page1.get_absolute_url("it"))
        response.render()
        self.assertContains(response, '<meta name="twitter:description" content="twitter - lorem ipsum - italian">')
        self.assertContains(response, '<meta itemprop="description" content="gplus - lorem ipsum - italian">')
        self.assertContains(response, '<meta property="og:description" content="opengraph - lorem ipsum - italian">')
        self.assertContains(response, '<meta property="og:title" content="pagina uno">')
        self.assertContains(
            response, '<meta property="og:url" content="http://example.com%s">' % page1.get_absolute_url("it")
        )
        self.assertContains(response, '<meta custom="attr" content="foo-it">')

        # English language
        response = self.client.get(page1.get_absolute_url("en"))
        self.assertContains(response, '<meta name="twitter:description" content="twitter - lorem ipsum - english">')
        self.assertContains(response, '<meta itemprop="description" content="gplus - lorem ipsum - english">')
        self.assertContains(response, '<meta property="og:description" content="opengraph - lorem ipsum - english">')
        self.assertContains(response, '<meta property="og:title" content="page one">')
        self.assertContains(
            response, '<meta property="og:url" content="http://example.com%s">' % page1.get_absolute_url("en")
        )
        self.assertContains(response, '<meta custom="attr" content="foo-en">')

    def test_fallbacks(self):
        """
        Test title-level templatetags
        """
        page1, page2 = self.create_pages()
        content_en = PageContent.admin_manager.get(page=page1, language="en")
        content_en.meta_description = self.title_data["description"]
        content_en.save()
        content_it = PageContent.admin_manager.get(page=page1, language="it")
        content_it.meta_description = self.title_data_it["description"]
        content_it.save()
        content_ext_en = TitleMeta.objects.create(extended_object=content_en)
        content_ext_en.save()
        content_ext_it = TitleMeta.objects.create(extended_object=content_it)
        content_ext_it.save()
        self.publish_page(page1, "it")
        self.publish_page(page1, "en")

        # page1 = page1.get_draft_object()
        content_en = page1.get_content_obj(language="en", fallback=False)
        content_ext_en = content_en.titlemeta

        # Italian language
        response = self.client.get(page1.get_absolute_url("it"))
        response.render()
        self.assertContains(response, '<meta name="description" content="base lorem ipsum - italian">')
        self.assertContains(response, '<meta name="twitter:description" content="base lorem ipsum - italian">')
        self.assertContains(response, '<meta itemprop="description" content="base lorem ipsum - italian">')
        self.assertContains(response, '<meta property="og:description" content="base lorem ipsum - italian">')
        self.assertContains(response, '<meta property="og:title" content="pagina uno">')
        self.assertContains(
            response, '<meta property="og:url" content="http://example.com%s">' % page1.get_absolute_url("it")
        )

        # English language
        response = self.client.get(page1.get_absolute_url("en"))
        self.assertContains(response, '<meta name="description" content="base lorem ipsum - english">')
        self.assertContains(response, '<meta name="twitter:description" content="base lorem ipsum - english">')
        self.assertContains(response, '<meta itemprop="description" content="base lorem ipsum - english">')
        self.assertContains(response, '<meta property="og:description" content="base lorem ipsum - english">')
        self.assertContains(response, '<meta property="og:title" content="page one">')
        self.assertContains(
            response, '<meta property="og:url" content="http://example.com%s">' % page1.get_absolute_url("en")
        )

        content_ext_en.description = "custom description"
        content_ext_en.save()
        # page1.publish("en")
        response = self.client.get(page1.get_absolute_url("en"))
        self.assertContains(response, '<meta name="description" content="custom description">')
        self.assertContains(response, '<meta name="twitter:description" content="custom description">')
        self.assertContains(response, '<meta itemprop="description" content="custom description">')

        # page1 = page1.get_draft_object()
        title_en = page1.get_content_obj(language="en", fallback=False)
        title_ext_en = title_en.titlemeta
        title_ext_en.twitter_description = "twitter custom description"
        title_ext_en.og_description = "og custom description"
        title_ext_en.save()
        # page1.publish("en")
        response = self.client.get(page1.get_absolute_url("en"))
        self.assertContains(response, '<meta name="description" content="custom description">')
        self.assertContains(response, '<meta name="twitter:description" content="twitter custom description">')
        self.assertContains(response, '<meta property="og:description" content="og custom description">')

        content2_en = PageContent.admin_manager.get(page=page2, language="en")
        content2_en.meta_description = self.title_data["description"]
        content2_en.save()
        self.publish_page(page2, "en")
        # English language
        # A page with no title meta, and yet the meta description is there
        response = self.client.get(page2.get_absolute_url("en"))
        self.assertContains(response, '<meta name="description" content="base lorem ipsum - english">')
        self.assertContains(response, '<meta name="twitter:description" content="base lorem ipsum - english">')
        self.assertContains(response, '<meta itemprop="description" content="base lorem ipsum - english">')
        self.assertContains(response, '<meta property="og:description" content="base lorem ipsum - english">')
        self.assertNotContains(response, '<meta property="og:title" content="page one">')
        self.assertNotContains(
            response, '<meta property="og:url" content="http://example.com%s">' % page1.get_absolute_url("en")
        )
