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
# Screen id, url, label, and the sections that screen contains. The sidebar
# renders the whole tree on every screen so the reader can see everything the
# dashboard holds and jump straight to any of it.
# Sections carry a Font Awesome name; CKAN 2.11 ships Font Awesome 6, and every
# name here was checked against its all.css rather than assumed.
NAV = [
    ('overview', '/insights', 'Overview', [
        ('weekly', 'Week by week', 'chart-column'),
        ('fleet', 'The fleet', 'server'),
        ('versions', 'Version spread', 'code-branch'),
    ]),
    ('trends', '/insights/trends', 'Trends', [
        ('changes', 'Version and plugin changes', 'clock-rotate-left'),
        ('ext-attention', 'Gaining attention', 'arrow-trend-up'),
        ('ext-downstream', 'Livelier downstream', 'code-pull-request'),
        ('adoption', 'Extension adoption (entry points)', 'puzzle-piece'),
    ]),
    ('instances', '/insights/instances', 'Instances', [
        ('instances', 'CKAN instances', 'table'),
        ('reliability', 'Sites crawl reliability', 'heart-pulse'),
        ('ext-all', 'Extensions', 'list-ul'),
    ]),
    ('discussion', '/insights/discussion', 'Discussion', []),
]

TABS = [(tab, url, label) for tab, url, label, _ in NAV]

# The standing forum thread for the dashboard:
# https://discuss.okfn.org/t/ckan-ecosystem-catalog-insights-discussion/13041
DISCUSSION_TOPIC_ID = '13041'


def _render(tab):
    return toolkit.render('insights/index.html', extra_vars={
        'tab': tab,
        'insights_tabs': TABS,
        'insights_nav': NAV,
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
