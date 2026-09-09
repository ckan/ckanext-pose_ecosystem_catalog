"""
Insights Blueprint - Routes for the CKAN ecosystem insights dashboard.

This module provides a Flask blueprint route for:
- /insights - The weekly crawl dashboard

The page carries no data of its own. It fetches
dashboard-data/dashboard.json from dathere/pose-ckanext-metadata, which the
ecosystem rollup workflow rebuilds and commits after each weekly crawl -- the
same arrangement templates/ckan_map/map.html already uses for the site
GeoJSON. Nothing here needs a redeploy when the numbers change.
"""
import logging
from flask import Blueprint

import ckan.plugins.toolkit as toolkit

log = logging.getLogger(__name__)

insights = Blueprint('insights', __name__)


@insights.route('/insights')
def insights_view():
    """Render the insights dashboard page."""
    return toolkit.render('insights/index.html')


def get_blueprints():
    """Return the list of blueprints for this module."""
    return [insights]
