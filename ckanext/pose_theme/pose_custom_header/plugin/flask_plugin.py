# -*- coding: utf-8 -*-
import ckan.plugins as p
from ckan.views.resource import Blueprint
from ckanext.pose_theme.pose_custom_header.controller import CustomHeaderController


class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IBlueprint)

    # IBlueprint
    def get_blueprint(self):
        return og_header


og_header = Blueprint('custom-header', __name__, url_prefix='/ckan-admin')

og_header.add_url_rule('/custom_header', methods=['GET', 'POST'],
                       view_func=CustomHeaderController().custom_header)
og_header.add_url_rule('/reset_custom_header', methods=['GET', 'POST'],
                       view_func=CustomHeaderController().reset_custom_header)
