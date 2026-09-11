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


# The dashboard is split into three screens so it is not one long scroll.
# Every screen renders the same template and the same client-side data; the
# active tab decides which sections are shown.
TABS = [
    ('overview', '/insights', 'Overview'),
    ('trends', '/insights/trends', 'Trends'),
    ('instances', '/insights/instances', 'Instances'),
    ('discussion', '/insights/discussion', 'Discussion'),
]

# The standing forum thread for the dashboard:
# https://discuss.okfn.org/t/ckan-ecosystem-catalog-insights-discussion/13041
DISCUSSION_TOPIC_ID = '13041'


def _render(tab):
    return toolkit.render('insights/index.html', extra_vars={
        'tab': tab,
        'insights_tabs': TABS,
        'discussion_topic_id': DISCUSSION_TOPIC_ID,
    })


@insights.route('/insights')
def insights_view():
    """Render the overview screen: headline stats, weekly crawl, fleet, versions."""
    return _render('overview')


@insights.route('/insights/trends')
def insights_trends():
    """Render the trends screen: change ledger and extension adoption."""
    return _render('trends')


@insights.route('/insights/instances')
def insights_instances():
    """Render the instances screen: instance table and crawl reliability."""
    return _render('instances')


@insights.route('/insights/discussion')
def insights_discussion():
    """Render the discussion screen: the dashboard's Discourse thread."""
    return _render('discussion')


def get_blueprints():
    """Return the list of blueprints for this module."""
    return [insights]
