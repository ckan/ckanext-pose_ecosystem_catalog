"""
CKAN Map Blueprint - Routes for the CKAN ecosystem map.

This module provides a Flask blueprint route for:
- /map - The main map view
"""
import logging
from flask import Blueprint

import ckan.plugins.toolkit as toolkit

log = logging.getLogger(__name__)

ckan_map = Blueprint('ckan_map', __name__)


def _get_config(key, default=''):
    """Get configuration value from CKAN config."""
    return toolkit.config.get(key, default)


@ckan_map.route('/map')
def map_view():
    """Render the map page."""
    extra_vars = {
        'maptiler_key': _get_config('ckanext.pose_theme.maptiler_api_key', ''),
    }
    return toolkit.render('ckan_map/map.html', extra_vars=extra_vars)


def get_blueprints():
    """Return the list of blueprints for this module."""
    return [ckan_map]
