# -*- coding: utf-8 -*-
import ckan.plugins as p
from ckan.views.resource import Blueprint
from ckanext.pose_theme.pose_custom_homepage.controller import CustomHomepageController


class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IBlueprint)

    # IBlueprint
    def get_blueprint(self):
        return api


api = Blueprint('custom-homepage', __name__, url_prefix='/ckan-admin')

api.add_url_rule('/custom_homepage', methods=['GET', 'POST'],
                 view_func=CustomHomepageController().custom_homepage)
api.add_url_rule('/reset_custom_homepage', methods=['GET', 'POST'],
                 view_func=CustomHomepageController().reset_custom_homepage)
