# -*- coding: utf-8 -*-

import os
import sys
import json
import logging
from collections import OrderedDict

from six import string_types

import ckan.plugins as plugins
import ckan.plugins.toolkit as tk
import ckan.lib.plugins as lb
import ckan.lib.helpers as h


import ckanext.pose_theme.pose_custom_showcase.helpers as showcase_helpers
import ckanext.pose_theme.pose_custom_showcase.actions as actions

_ = tk._

log = logging.getLogger(__name__)

DATASET_TYPE_NAME = "showcase"


class PoseShowcasePlugin(plugins.SingletonPlugin, lb.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IFacets, inherit=True)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IActions, inherit=True)

    # IConfigurer
    def update_config(self, config):
        tk.add_template_directory(config, "templates")
        tk.add_public_directory(config, "public")
        tk.add_resource("assets", "showcase")

    # ITemplateHelpers
    def get_helpers(self):
        return {
            "facet_remove_field": showcase_helpers.facet_remove_field,
            "get_site_statistics": showcase_helpers.get_site_statistics,
            "get_showcase_wysiwyg_editor": showcase_helpers.get_wysiwyg_editor,
            "get_recent_showcase_list": showcase_helpers.get_recent_showcase_list,
            "get_package_showcase_list": showcase_helpers.get_package_showcase_list,
            "get_value_from_showcase_extras": showcase_helpers.get_value_from_showcase_extras,
            "scheming_groups_choices": showcase_helpers.scheming_groups_choices,
            "get_package_dict": showcase_helpers.get_package_dict,
            "get_image_url": showcase_helpers.get_image_url,
        }

    # IFacets
    def dataset_facets(self, facets_dict, package_type):
        """Only show tags for Showcase search list."""
        if package_type != DATASET_TYPE_NAME:
            return facets_dict
        return OrderedDict({"tags": _("Tags")})



    # IPackageController
    def before_dataset_search(self, search_params):
        """
        Modify search parameters before the search is executed.
        Only filter dataset types when on the dataset listing page (not search results).
        """
        # Add some debug logging
        log.debug(f"Request path: {tk.request.path if tk.request else 'None'}")
        log.debug(f"Request args: {tk.request.args if tk.request else 'None'}")
        
        # Only apply filtering if we're on the exact /dataset path
        if tk.request and tk.request.path == "/dataset":
            # Check if this is a search query vs dataset listing
            is_search_query = self._is_search_query()
            
            log.debug(f"Is search query: {is_search_query}")
            
            if not is_search_query:
                # This is the dataset listing page (/dataset), apply filtering
                current_fq = search_params.get('fq', '')
                
                # Try different field names - adjust based on your CKAN setup
                type_filter = 'dataset_type:dataset'  # or 'type:dataset'
                
                if current_fq:
                    search_params['fq'] = f"{current_fq} AND {type_filter}"
                else:
                    search_params['fq'] = type_filter
                    
                log.debug(f"Applied filter: {search_params['fq']}")
        
        return search_params

    def _is_search_query(self):
        """
        Check if the current request is a search query or just dataset listing.
        Returns True if it's a search, False if it's just the dataset listing page.
        """
        try:
            # Use CKAN's toolkit request
            if tk.request and tk.request.args:
                # Check for 'q' parameter (main search)
                if tk.request.args.get('q'):
                    return True
                
                # Check for other search-related parameters
                search_params = ['fq', 'sort', 'ext_bbox']
                for param in search_params:
                    if tk.request.args.get(param):
                        return True
                
            
            return False
        except Exception as e:
            # Log the error for debugging
            log.debug(f"Error checking search query: {e}")
            return False

    def after_dataset_search(self, search_results, search_params):
        """
        Modify search results after the search is executed.
        """
        return search_results

    # IActions
    def get_actions(self):
        return {
            "ckanext_showcase_list": actions.showcase_list,
        }