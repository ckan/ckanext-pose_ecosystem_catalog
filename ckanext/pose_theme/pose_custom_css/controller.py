# encoding: utf-8
from collections import OrderedDict

import ckan.plugins.toolkit as tk
from ckan import model

from ckanext.pose_theme.base.compatibility_controller import BaseCompatibilityController
from ckanext.pose_theme.pose_custom_css.processor import custom_style_processor
from ckanext.pose_theme.pose_custom_css.constants import (
    CSS_METADATA, RAW_CSS,
    ACCOUNT_HEADER_FIELDS, NAVIGATION_HEADER_FIELDS,
    MODULE_HEADER_FIELDS, FOOTER_FIELDS
)


class CustomCSSController(BaseCompatibilityController):
    def custom_css(self):
        try:
            context = {'model': model, 'user': tk.c.user}
            tk.check_access('sysadmin', context, {})
        except tk.NotAuthorized:
            tk.abort(403, tk._('Need to be system administrator to administer'))
        css_metadata = self.get_data(CSS_METADATA)
        if not css_metadata:
            # This case can happen only during the cold start on empty DB.
            default_raw_css, css_metadata = custom_style_processor.get_custom_css({})
            self.save_css_metadata(default_raw_css, css_metadata)

        if tk.request.method == 'POST':
            form_data = self.get_form_data(tk.request)
            custom_css, css_metadata = custom_style_processor.get_custom_css(form_data)

            try:
                custom_style_processor.check_contrast()
                self.save_css_metadata(custom_css, css_metadata)

                tk.get_action('config_option_update')(context, {
                    'ckan.site_custom_css': form_data.get('ckan.site_custom_css')
                })
            except tk.ValidationError as e:
                errors = e.error_dict
                extra_vars = {'data': form_data, 'errors': errors}
                extra_vars.update(self.get_form_fields(css_metadata))
                return tk.render('admin/custom_css_form.html', extra_vars=extra_vars)

        site_custom_css = tk.get_action('config_option_show')(context, {
            'key': 'ckan.site_custom_css'
        })

        data = {'ckan.site_custom_css': site_custom_css}
        extra_vars = {'data': data, 'errors': {}}
        extra_vars.update(self.get_form_fields(css_metadata))
        return tk.render('admin/custom_css_form.html', extra_vars=extra_vars)

    def reset_custom_css(self):
        try:
            context = {'model': model, 'user': tk.c.user}
            tk.check_access('sysadmin', context, {})
        except tk.NotAuthorized:
            tk.abort(403, tk._('Need to be system administrator to administer'))

        default_raw_css, default_css_metadata = custom_style_processor.get_custom_css({})
        self.save_css_metadata(default_raw_css, default_css_metadata)

        if tk.check_ckan_version(min_version='2.9.0'):
            custom_css_route = 'custom-css.custom_css'
        else:
            custom_css_route = 'custom_css'
        return tk.redirect_to(custom_css_route)

    def save_css_metadata(self, custom_css, css_metadata):
        self.store_data(RAW_CSS, custom_css)
        metadata = self.sort_inputs_by_title(css_metadata)
        self.store_data(CSS_METADATA, metadata)

    @staticmethod
    def get_raw_css():
        return tk.get_action('config_option_show')({'ignore_auth': True}, {'key': RAW_CSS})

    @staticmethod
    def get_form_fields(css_metadata):
        account_header_fields = OrderedDict()
        navigation_header_fields = OrderedDict()
        module_header_fields = OrderedDict()
        footer_fields = OrderedDict()
        for key, value in css_metadata.items():
            if key in ACCOUNT_HEADER_FIELDS:
                account_header_fields[key] = value
            if key in NAVIGATION_HEADER_FIELDS:
                navigation_header_fields[key] = value
            if key in MODULE_HEADER_FIELDS:
                module_header_fields[key] = value
            if key in FOOTER_FIELDS:
                footer_fields[key] = value
        return {
            'account_header_fields': account_header_fields,
            'navigation_header_fields': navigation_header_fields,
            'module_header_fields': module_header_fields,
            'footer_fields': footer_fields
        }

    @staticmethod
    def sort_inputs_by_title(css_metadata):
        sorted_list = [(key, value) for key, value in css_metadata.items()]
        sorted_list = sorted(sorted_list, key=lambda x: x[1].get('title', ''))
        return OrderedDict(sorted_list)
