from ckan.controllers.package import PackageController

import ckanext.pose_theme.pose_custom_heroslider.utils as utils


class HeroSliderAdminController(PackageController):
    def hero_slider_admin(self):
        return utils.hero_slider_admin()
