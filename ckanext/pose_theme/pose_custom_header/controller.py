# encoding: utf-8
from copy import deepcopy

import ckan.plugins.toolkit as tk
from ckan import model

import ckanext.pose_theme.base.helpers as helper
from ckanext.pose_theme.pose_custom_header.constants import CONFIG_SECTION
from ckanext.pose_theme.base.compatibility_controller import BaseCompatibilityController


class CustomHeaderController(BaseCompatibilityController):
    default_header = {
        'layout_type': 'default',
        'links': [
            {'position': 0, 'title': 'Datasets', 'url': '/dataset'},
            {'position': 1, 'title': '{}s'.format(helper.get_organization_alias()), 'url': '/organization'},
            {'position': 2, 'title': '{}s'.format(helper.get_group_alias()), 'url': '/group'},
            {'position': 3, 'title': 'About', 'url': '/about'}
        ]
    }

    def custom_header(self):
        try:
            context = {'model': model, 'user': tk.c.user}
            tk.check_access('sysadmin', context, {})
        except tk.NotAuthorized:
            tk.abort(403, tk._('Need to be system administrator to administer'))

        custom_header = self.get_custom_header_metadata()

        if tk.request.method == 'POST':
            data = self.get_form_data(tk.request)
            if 'save' in data:
                custom_header = self.save_link(data)
            elif 'add_link' in data:
                custom_header = self.add_link(data, custom_header)
            elif 'remove_link' in data:
                custom_header = self.remove_link(data, custom_header)

        return tk.render('admin/custom_header_form.html',
                         extra_vars=custom_header)

    def save_link(self, data):
        custom_header = {
            'layout_type': data.get('layout_type', 'default'),
            'links': []
        }
        try:
            if isinstance(data.get('url'), list):
                for index in range(len(data.get('url'))):
                    custom_header['links'].append(
                        {
                            'position': data['position'][index],
                            'title': data['title'][index],
                            'url': data['url'][index]
                        }
                    )
            elif data.get('position') and data.get('title') and data.get('url'):
                custom_header['links'].append(
                    {
                        'position': data['position'],
                        'title': data['title'],
                        'url': data['url']
                    }
                )
            errors = self.save_custom_header_metadata(custom_header)
            custom_header['errors'] = errors
        except tk.ValidationError as err:
            custom_header['errors'] = err.error_dict
        return custom_header

    def add_link(self, data, old_header):
        new_header = deepcopy(old_header)
        new_header.get('links', []).append(
            {
                'position': len(new_header.get('links', [])),
                'title': data.get('new_title'),
                'url': data.get('new_url')
            }
        )
        try:
            errors = self.save_custom_header_metadata(new_header)
        except tk.ValidationError as err:
            errors = err.error_dict
        if errors:
            old_header.update({
                'errors': errors,
                'new_title': data.get('new_title', ''),
                'url': data.get('new_url', '')
            })
            return old_header
        return new_header

    def remove_link(self, data, old_header):
        new_header = deepcopy(old_header)
        try:
            item = [link for link in new_header['links'] if link.get('title') == data['remove_title']]
            new_header['links'].remove(item[0])
            errors = self.save_custom_header_metadata(new_header)
        except tk.ValidationError as err:
            errors = err.error_dict
        except IndexError:
            errors = {'Remove Nav Link': 'No link to remove.'}
        if errors:
            old_header['errors'] = errors
            return old_header
        return new_header

    def reset_custom_header(self):
        try:
            context = {'model': model, 'user': tk.c.user}
            tk.check_access('sysadmin', context, {})
        except tk.NotAuthorized:
            tk.abort(403, tk._('Need to be system administrator to administer'))

        self.save_custom_header_metadata(CustomHeaderController.default_header)

        if tk.check_ckan_version(min_version='2.9.0'):
            custom_header_route = 'custom-header.custom_header'
        else:
            custom_header_route = 'custom_header'
        return tk.redirect_to(custom_header_route)

    def save_custom_header_metadata(self, custom_header):
        try:
            CustomHeaderController.store_data(CONFIG_SECTION, custom_header)
        except tk.ValidationError as err:
            return err.error_summary or err.error_dict

    def get_custom_header_metadata(self):
        data_dict = CustomHeaderController.get_data(CONFIG_SECTION)
        if not data_dict:
            data_dict = CustomHeaderController.default_header.copy()
        return data_dict
