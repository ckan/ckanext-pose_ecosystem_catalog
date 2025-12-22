# encoding: utf-8
import logging

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

import ckanext.pose_theme.pose_custom_heroslider.actions as actions
import ckanext.pose_theme.pose_custom_heroslider.auth as auth
import ckanext.pose_theme.pose_custom_heroslider.db as db
import ckanext.pose_theme.pose_custom_heroslider.helpers as helpers

if toolkit.check_ckan_version(min_version="2.9.0"):
    from ckanext.pose_theme.pose_custom_heroslider.plugin.flask_plugin import (
        MixinPlugin,
    )
else:
    from ckanext.pose_theme.pose_custom_heroslider.plugin.pylons_plugin import (
        MixinPlugin,
    )


log = logging.getLogger(__name__)


class PoseHeroSliderPlugin(MixinPlugin, plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IAuthFunctions, inherit=True)
    plugins.implements(plugins.IActions)

    # IConfigurer
    def update_config(self, config):
        toolkit.add_template_directory(config, "../templates")
        toolkit.add_public_directory(config, "../public")
        toolkit.add_resource("../assets", "pose_custom_heroslider")


    # IConfigurable
    def configure(self, config):
        db.init()

    # ITemplateHelpers
    def get_helpers(self):
        return {
            "hero_dataset_count": helpers.dataset_count,
            "hero_get_hero_images": helpers.get_hero_images,
            "hero_get_hero_text": helpers.get_hero_text,
            "hero_get_max_image_size": helpers.get_max_image_size,
        }

    # IAuthFunctions
    def get_auth_functions(self):
        return {
            "hero_slider_update": auth.hero_slider_update,
            "hero_slider_list": actions.hero_slider_list,
        }

    # IActions
    def get_actions(self):
        action_functions = {
            "hero_slider_update": actions.hero_slider_update,
            "hero_slider_list": actions.hero_slider_list,
        }
        return action_functions
