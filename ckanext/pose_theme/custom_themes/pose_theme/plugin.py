import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckanext.pose_theme.base.helpers as helper
import ckanext.pose_theme.custom_themes.pose_theme.blueprint as view
import ckanext.pose_theme.custom_themes.pose_theme.ckan_map_blueprint as ckan_map
import ckanext.pose_theme.custom_themes.pose_theme.insights_blueprint as insights
import ckanext.pose_theme.custom_themes.pose_theme.cli as cli
from ckanext.pose_theme.routes import contact

# ckanext-discourse stores the topic id it creates on the package via
# package_update. site/extension/tool declare topic_id in their own
# schemas; the plain `dataset` type is validated against ckanext-dcat's
# dcat_ap_recommended.yaml, which we don't own, so the key was silently
# dropped and the topic never linked back.
TOPIC_ID_FIELD = {
    'field_name': 'topic_id',
    'label': 'Topic ID',
    'validators': 'ignore_missing',
    'form_snippet': None,
    'display_snippet': None,
}


def add_topic_id_field(schema):
    """Append topic_id to a scheming schema unless it already has it."""
    fields = schema['dataset_fields']
    if not any(f.get('field_name') == 'topic_id' for f in fields):
        fields.append(dict(TOPIC_ID_FIELD))
    return schema


class PoseThemePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IFacets, inherit=True)
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IConfigurable)

    # IFacets
    def dataset_facets(self, facets_dict, package_type):
        """Customize the facets displayed for datasets."""
        if facets_dict is None:
            facets_dict = {}
        if package_type in ("site", "tool"):
            if "license_id" in facets_dict:
                del facets_dict["license_id"]
            if "res_format" in facets_dict:
                del facets_dict["res_format"]
        # Return the modified facets dictionary
        return facets_dict

    # IConfigurer
    def update_config(self, ckan_config):
        toolkit.add_template_directory(ckan_config, 'templates')
        toolkit.add_public_directory(ckan_config, 'public')
        toolkit.add_resource('assets', 'pose_theme')
        toolkit.add_public_directory(ckan_config, "assets")

    def update_config_schema(self, schema):
        ignore_missing = toolkit.get_validator('ignore_missing')
        ignore_not_sysadmin = toolkit.get_validator('ignore_not_sysadmin')
        schema.update({
            # This is a custom configuration option
            'contact_form_legend_content': [ignore_missing, ignore_not_sysadmin],
            # MapTiler API key for the CKAN ecosystem map
            'ckanext.pose_theme.maptiler_api_key': [ignore_missing, ignore_not_sysadmin],
        })
        return schema

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'pose_theme_group_alias': helper.get_group_alias,
            'pose_theme_organization_alias': helper.get_organization_alias,
            'pose_theme_get_default_extent': helper.get_default_extent,
            'pose_theme_is_data_dict_active': helper.is_data_dict_active,
            'version': helper.version_builder,
            'pose_theme_get_maptiler_api_key': helper.get_maptiler_api_key,
            'get_latest_editor': helper.get_latest_editor,
            'pose_theme_tools': helper.tools,
            'pose_theme_featured_tools': helper.featured_tools,
            'pose_theme_recent_tools': helper.recent_tools,
            'pose_theme_get_user_organizations': helper.get_user_organizations,
            'pose_theme_thumbnail_url': helper.get_thumbnail_url,
        }

    def get_commands(self):
        return [cli.pose_theme]

    # IBlueprint
    def get_blueprint(self):
        # Combine all blueprint lists
        blueprints = view.get_blueprints()
        blueprints.extend(contact.get_blueprints())
        # ckan_map_blueprint has existed since the map was built but was never
        # imported here, so /map has been a 404 in production. The homepage
        # embeds its own copy of the map, which is why nobody noticed.
        blueprints.extend(ckan_map.get_blueprints())
        blueprints.extend(insights.get_blueprints())
        return blueprints

    # IConfigurable
    def configure(self, config):
        # Patch the loaded schema rather than forking upstream's YAML.
        # ponytail: uses scheming's _expanded_schemas; if that attribute
        # goes away, copy dcat_ap_recommended.yaml into this extension
        # and point scheming.dataset_schemas at the copy.
        try:
            from ckanext.scheming.plugins import SchemingDatasetsPlugin
            schemas = SchemingDatasetsPlugin.instance._expanded_schemas
            schema = schemas['dataset']
        except (ImportError, AttributeError, KeyError, TypeError):
            return
        add_topic_id_field(schema)

    # IPackageController
    def before_dataset_update(self, context, data_dict):
        # topic_id has no form snippet, so an ordinary edit-form save
        # submits without it and validation would drop the extra,
        # unlinking the Discourse topic. Carry the stored value over.
        if data_dict.get('topic_id') or not data_dict.get('id'):
            return data_dict
        try:
            current = toolkit.get_action('package_show')(
                {'ignore_auth': True}, {'id': data_dict['id']})
        except Exception:
            return data_dict
        if current.get('topic_id'):
            data_dict['topic_id'] = current['topic_id']
        return data_dict

    def after_dataset_show(self, context, pkg_dict):
        # Ensure topic_id is present so ckanext-discourse doesn't crash on
        # site/extension/tool packages that were saved before the field existed.
        pkg_dict.setdefault('topic_id', '')