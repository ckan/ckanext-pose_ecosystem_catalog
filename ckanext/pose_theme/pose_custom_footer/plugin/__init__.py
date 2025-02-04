import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

import ckanext.pose_theme.base.helpers as helper
from ckanext.pose_theme.pose_custom_footer.controller import CustomFooterController
from ckanext.pose_theme.pose_custom_footer.constants import CONFIG_KEY

if toolkit.check_ckan_version(min_version='2.9.0'):
    from ckanext.pose_theme.pose_custom_footer.plugin.flask_plugin import MixinPlugin
    from ckan.lib.helpers import literal
else:
    from ckanext.pose_theme.pose_custom_footer.plugin.pylons_plugin import MixinPlugin
    from webhelpers.html import literal


class PoseThemeFooterPlugin(MixinPlugin):
    plugins.implements(plugins.IConfigurable, inherit=True)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IValidators)

    # IConfigurer
    def update_config(self, ckan_config):
        toolkit.add_template_directory(ckan_config, '../templates')
        toolkit.add_public_directory(ckan_config, '../assets')
        toolkit.add_resource('../assets', 'pose_custom_footer_resource')
        toolkit.add_ckan_admin_tab(ckan_config, 'custom-footer.custom_footer',
                                   'Footer', icon='file-code-o')

    def update_config_schema(self, schema):
        ignore_missing = toolkit.get_validator('ignore_missing')
        dict_only = toolkit.get_validator('dict_only')
        schema.update({
            # This is a custom configuration option
            CONFIG_KEY: [ignore_missing, dict_only, custom_footer_validator],
        })
        return schema

    # IValidators
    def get_validators(self):
        return {
            u'custom_footer_validator': custom_footer_validator,
        }

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'pose_theme_get_footer_data': get_footer_data,
            'version': helper.version_builder,
            'get_column_count': helper.get_column_count,
        }


def get_footer_data(section):
    data_dict = CustomFooterController.get_custom_footer_metadata()
    if data_dict.get(section):
        return literal(data_dict.get(section))
    return ''


def custom_footer_validator(value):
    layout_type = value.get('layout_type')
    if layout_type not in ['default', 'custom']:
        raise toolkit.Invalid('Invalid footer layout')

    # content is sanitized by controller soo only taught validation required
    content_0 = value.get('content_0')
    if helper.check_characters(content_0):
        raise toolkit.Invalid('Invalid characters in Column 1')
    content_1 = value.get('content_1')
    if helper.check_characters(content_1):
        raise toolkit.Invalid('Invalid characters in Column 2')
    return value
