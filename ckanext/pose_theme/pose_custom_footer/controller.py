# encoding: utf-8
import bleach
import ckan.plugins.toolkit as tk
from ckan import model

from ckanext.pose_theme.pose_custom_footer.constants import (
    CONFIG_KEY,
    ALLOWED_TAGS_SET,
    ALLOWED_TAGS_LIST,
    ALLOWED_ATTRIBUTES,
    ALLOWED_CSS_PROPERTIES
)
from ckanext.pose_theme.base.compatibility_controller import BaseCompatibilityController


def clean_html(text):
    try:
        from bleach.css_sanitizer import CSSSanitizer
        CSS_Sanitizer = CSSSanitizer(allowed_css_properties=ALLOWED_CSS_PROPERTIES)
        return bleach.clean(text, tags=ALLOWED_TAGS_SET, attributes=ALLOWED_ATTRIBUTES, css_sanitizer=CSS_Sanitizer)
    except ImportError:
        return bleach.clean(text, tags=ALLOWED_TAGS_LIST, attributes=ALLOWED_ATTRIBUTES, styles=ALLOWED_CSS_PROPERTIES)


class CustomFooterController(BaseCompatibilityController):
    default_footer = {'layout_type': 'default', 'content_0': '', 'content_1': '', 'content_2': ''}

    def custom_footer(self):
        try:
            context = {'model': model, 'user': tk.c.user}
            tk.check_access('sysadmin', context, {})
        except tk.NotAuthorized:
            tk.abort(403, tk._('Need to be system administrator to administer'))

        custom_footer = self.get_custom_footer_metadata()

        if tk.request.method == 'POST':
            data = self.get_form_data(tk.request)
            custom_footer = {
                'layout_type': data.get('layout_type', 'default'),
                'content_0': clean_html(data.get('content_0', '')),
                'content_1': clean_html(data.get('content_1', '')),
                'content_2': clean_html(data.get('content_2', '')),
                'content_3': clean_html(data.get('content_3', ''))
            }
            error = self.save_footer_metadata(custom_footer)
            custom_footer['errors'] = error

        return tk.render('admin/custom_footer_form.html',
                         extra_vars=dict(data=custom_footer))

    def reset_custom_footer(self):
        try:
            context = {'model': model, 'user': tk.c.user}
            tk.check_access('sysadmin', context, {})
        except tk.NotAuthorized:
            tk.abort(403, tk._('Need to be system administrator to administer'))

        self.save_footer_metadata(CustomFooterController.default_footer)

        if tk.check_ckan_version(min_version='2.9.0'):
            custom_footer_route = 'custom-footer.custom_footer'
        else:
            custom_footer_route = 'custom_footer'
        return tk.redirect_to(custom_footer_route)

    @staticmethod
    def save_footer_metadata(custom_footer):
        try:
            CustomFooterController.store_data(CONFIG_KEY, custom_footer)
        except tk.ValidationError as ex:
            return ex.error_summary

    @staticmethod
    def get_custom_footer_metadata():
        data = CustomFooterController.get_data(CONFIG_KEY)
        if not data:
            data = CustomFooterController.default_footer.copy()
        return data
