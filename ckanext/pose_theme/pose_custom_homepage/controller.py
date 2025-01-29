# encoding: utf-8
from collections import OrderedDict

import ckan.plugins.toolkit as tk
from ckan import model

from ckanext.pose_theme.pose_custom_homepage.constants import LAYOUTS, CUSTOM_STYLE, CUSTOM_NAMING
from ckanext.pose_theme.pose_custom_homepage.processor import custom_naming_processor
from ckanext.pose_theme.base.compatibility_controller import BaseCompatibilityController


class CustomHomepageController(BaseCompatibilityController):
    def custom_homepage(self):
        try:
            context = {'model': model, 'user': tk.c.user}
            tk.check_access('sysadmin', context, {})
        except tk.NotAuthorized:
            tk.abort(403, tk._('Need to be system administrator to administer'))

        if tk.request.method == 'POST':
            data = self.get_form_data(tk.request)
            self.store_config(data)

        # Get last or default layout
        actual_layout = self.get_data(CUSTOM_STYLE)
        if not actual_layout:
            actual_layout = 1

        # Get last or default custom naming
        custom_naming = self.get_data(CUSTOM_NAMING)
        if not custom_naming:
            custom_naming = custom_naming_processor.get_custom_naming({})
            self.store_data(config_key=CUSTOM_NAMING, data=custom_naming)
        custom_naming = self.reorder_fields(custom_naming)

        return tk.render(
            'admin/custom_homepage_form.html',
            extra_vars={
                'home_page_layouts_list': LAYOUTS,
                'actual_layout': actual_layout,
                'custom_naming': custom_naming
            }
        )

    def reset_custom_homepage(self):
        try:
            context = {'model': model, 'user': tk.c.user}
            tk.check_access('sysadmin', context, {})
        except tk.NotAuthorized:
            tk.abort(403, tk._('Need to be system administrator to administer'))

        self.store_data(CUSTOM_STYLE, 1)

        naming = custom_naming_processor.get_custom_naming({})
        naming = self.reorder_fields(naming)
        self.store_data(CUSTOM_NAMING, naming)

        if tk.check_ckan_version(min_version='2.9.0'):
            custom_homepage_route = 'custom-homepage.custom_homepage'
        else:
            custom_homepage_route = 'custom_homepage'
        return tk.redirect_to(custom_homepage_route)

    def store_config(self, data):
        # Check and update home page layout style
        layout_style = data.get('custom_homepage_layout')
        if layout_style:
            self.store_data(CUSTOM_STYLE, layout_style)

        # Parse and save naming
        naming = custom_naming_processor.get_custom_naming(data)
        self.store_data(CUSTOM_NAMING, naming)

    @staticmethod
    def reorder_fields(names):
        field_order = [
            'groups-custom-name', 'showcases-custom-name',
            'popular-datasets-custom-name', 'recent-datasets-custom-name'
        ]
        sorted_fields = []
        for field_name in field_order:
            sorted_fields += [(key, value) for key, value in names.items() if key == field_name]
        return OrderedDict(sorted_fields)
