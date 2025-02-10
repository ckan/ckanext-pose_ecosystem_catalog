# -*- coding: utf-8 -*-
import ckan.plugins as p
from ckan.views.resource import Blueprint
from ckanext.pose_theme.pose_custom_css.controller import CustomCSSController


class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IBlueprint)

    # IBlueprint
    def get_blueprint(self):
        return api


api = Blueprint('custom-css', __name__, url_prefix='/ckan-admin')
api.add_url_rule('/custom_css', methods=['GET', 'POST'],
                 view_func=CustomCSSController().custom_css)
api.add_url_rule('/reset_custom_css', methods=['GET', 'POST'],
                 view_func=CustomCSSController().reset_custom_css)
