from cms.cms_toolbars import PAGE_MENU_SECOND_BREAK
from cms.models import PageContent
from cms.toolbar.items import Break
from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool
from cms.utils.conf import get_cms_setting
from cms.utils.i18n import get_language_list, get_language_object
from cms.utils.permissions import has_page_permission
from django.urls import NoReverseMatch, reverse
from django.utils.translation import gettext_lazy as _

from .models import DefaultMetaImage, PageMeta, TitleMeta

PAGE_META_MENU_TITLE = _("Meta-information")
PAGE_META_ITEM_TITLE = _("Common")
PAGE_META_DEFAULT_META_IMAGE_TITLE = _("Default meta image")


@toolbar_pool.register
class PageToolbarMeta(CMSToolbar):
    def populate(self):
        self.page = self.request.current_page
        if not self.page:
            # Nothing to do
            return
        if self.page.is_page_type:
            # we don't need this on page types
            return

        # check global permissions if CMS_PERMISSIONS is active
        if get_cms_setting("PERMISSION"):
            has_global_current_page_change_permission = has_page_permission(
                self.request.user, self.request.current_page, "change_page"
            )
        else:
            has_global_current_page_change_permission = False
            # check if user has page edit permission
        permission = self.page.has_change_permission(self.request.user)
        can_change = self.page and permission
        if has_global_current_page_change_permission or can_change:

            current_page_menu = self.toolbar.get_or_create_menu("page")
            super_item = current_page_menu.find_first(Break, identifier=PAGE_MENU_SECOND_BREAK)
            if super_item:
                super_item = super_item + 1
            meta_menu = current_page_menu.get_or_create_menu("pagemeta", PAGE_META_MENU_TITLE, position=super_item)
            position = 0
            # Page tags
            default_meta_image = DefaultMetaImage.objects.first()
            if default_meta_image:
                meta_menu.add_modal_item(
                    PAGE_META_DEFAULT_META_IMAGE_TITLE,
                    url=reverse("admin:djangocms_page_meta_defaultmetaimage_change", args=(default_meta_image.pk,)),
                    position=position,
                )
                position += 1
            try:
                page_extension = PageMeta.objects.get(extended_object_id=self.page.pk)
            except PageMeta.DoesNotExist:
                page_extension = None
            try:
                if page_extension:
                    url = reverse("admin:djangocms_page_meta_pagemeta_change", args=(page_extension.pk,))
                else:
                    url = "{}?extended_object={}".format(
                        reverse("admin:djangocms_page_meta_pagemeta_add"), self.page.pk
                    )
            except NoReverseMatch:
                # not in urls
                pass
            else:
                meta_menu.add_modal_item(PAGE_META_ITEM_TITLE, url=url, position=position)
            # Content tags
            site_id = self.page.node.site_id

            contents = PageContent.admin_manager.filter(
                page=self.page, language__in=get_language_list(site_id)
            ).current_content()

            # TODO: rename to content extensions
            title_extensions = {
                t.extended_object_id: t
                for t in TitleMeta.objects.filter(extended_object_id__in=[content.id for content in contents])
            }

            for content in contents:
                try:
                    if content.pk in title_extensions:
                        url = reverse(
                            "admin:djangocms_page_meta_titlemeta_change", args=(title_extensions[content.pk].pk,)
                        )
                    else:
                        url = "{}?extended_object={}".format(
                            reverse("admin:djangocms_page_meta_titlemeta_add"), content.pk
                        )
                except NoReverseMatch:
                    # not in urls
                    pass
                else:
                    position += 1
                    language = get_language_object(content.language)
                    meta_menu.add_modal_item(language["name"], url=url, position=position)
