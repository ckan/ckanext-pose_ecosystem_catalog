"""
CKAN Map Blueprint - Routes for the CKAN ecosystem map.

This module provides Flask blueprint routes for:
- /map - The main map view
- /map/sites.geojson - GeoJSON API endpoint for site locations
- /map/stats - JSON API for extension and site counts
"""
import logging
import requests
from flask import Blueprint, jsonify

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


@ckan_map.route('/map/sites.geojson')
def site_geojson():
    """
    Fetch all CKAN sites from the catalog and return as GeoJSON.
    Uses the local CKAN API to fetch sites with type=site.
    """
    geojson = {"type": "FeatureCollection", "features": []}

    rows = 500
    start = 0
    site_url = _get_config('ckan.site_url', '')

    while True:
        try:
            result = toolkit.get_action('package_search')(
                {},
                {
                    'fq': 'type:site',
                    'rows': rows,
                    'start': start,
                }
            )
            records = result.get('results', [])

            if not records:
                break

            start += rows

            for row in records:
                try:
                    lat = row.get('latitude')
                    lon = row.get('longitude')

                    if lat is None or lon is None:
                        continue

                    geojson["features"].append({
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [float(lon), float(lat)],
                        },
                        "properties": {
                            "id": row.get("id", ""),
                            "name": row.get("name", ""),
                            "title": row.get("title", ""),
                            "url": row.get("url", ""),
                            "catalog_url": f"{site_url}/site/{row.get('name', '')}",
                            "state": row.get("state", ""),
                            "description": row.get("notes", ""),
                            "num_datasets": row.get("num_datasets", 0),
                            "num_organizations": row.get("num_organizations", 0),
                            "num_resources": row.get("num_resources", 0),
                        },
                    })
                except (KeyError, ValueError, TypeError) as e:
                    log.warning(f"Skipping site with invalid data: {e}")
                    continue

        except Exception as e:
            log.error(f"Failed to fetch sites: {e}")
            return jsonify({"error": f"Failed to fetch data: {str(e)}"}), 502

    return jsonify(geojson)


@ckan_map.route('/map/stats')
def catalog_stats():
    """
    Fetch extension and site counts from the catalog.
    """
    try:
        # Fetch extension count
        ext_result = toolkit.get_action('package_search')(
            {},
            {'fq': 'type:extension', 'rows': 0}
        )
        extensions = ext_result.get('count', 0)

        # Fetch site count
        site_result = toolkit.get_action('package_search')(
            {},
            {'fq': 'type:site', 'rows': 0}
        )
        sites = site_result.get('count', 0)

        return jsonify({
            "extensions": extensions,
            "sites": sites,
        })

    except Exception as e:
        log.error(f"Failed to fetch stats: {e}")
        return jsonify({"error": f"Failed to fetch stats: {str(e)}"}), 502


def get_blueprints():
    """Return the list of blueprints for this module."""
    return [ckan_map]
