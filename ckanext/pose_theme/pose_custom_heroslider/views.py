# encoding: utf-8
from flask import Blueprint
import ckanext.pose_theme.pose_custom_heroslider.utils as utils


heroslideradmin = Blueprint("heroslideradmin_blueprint", __name__)


def hero_slider_admin():
    return utils.hero_slider_admin()


heroslideradmin.add_url_rule(
    "/ckan-admin/hero_slider_admin",
    view_func=hero_slider_admin,
    methods=["GET", "POST"],
)


def get_blueprints():
    return [heroslideradmin]
