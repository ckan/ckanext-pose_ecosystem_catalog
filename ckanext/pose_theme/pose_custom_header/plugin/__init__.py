import string
from six.moves.urllib.parse import urlparse

import ckan.plugins as plugins
import ckan.plugins.toolkit as tk

import ckanext.pose_theme.base.helpers as helper
from ckanext.pose_theme.pose_custom_header.controller import CustomHeaderController
from ckanext.pose_theme.pose_custom_header.constants import CONFIG_SECTION

try:
    from html import escape as html_escape
except ImportError:
    from cgi import escape as html_escape  # noqa: F401

from ckanext.pose_theme.pose_custom_header.plugin.flask_plugin import MixinPlugin
from ckan.lib.helpers import literal


class PoseThemeHeaderPlugin(MixinPlugin):
    plugins.implements(plugins.IConfigurable, inherit=True)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IValidators)

    # IConfigurer
    def update_config(self, ckan_config):
        tk.add_template_directory(ckan_config, "../templates")

    def update_config_schema(self, schema):
        ignore_missing = tk.get_validator("ignore_missing")
        dict_only = tk.get_validator("dict_only")
        schema.update(
            {CONFIG_SECTION: [ignore_missing, dict_only, custom_header_validator]}
        )
        return schema

    # ITemplateHelpers
    def get_helpers(self):
        return {
            "pose_theme_build_nav_main": build_nav_main,
            "pose_theme_get_header_layout": get_header_layout,
            "pose_theme_group_alias": helper.get_group_alias,
            "pose_theme_organization_alias": helper.get_organization_alias,
            "version": helper.version_builder,
        }

    # IValidators
    def get_validators(self):
        return {
            "custom_header_url_validator": custom_header_validator,
        }


def build_nav_main(*args):
    controller = CustomHeaderController()
    custom_header = controller.get_custom_header_metadata()
    header_links = [item for item in custom_header.get("links", [])]
    header_links.sort(key=lambda x: int(x.get("position", 0)))

    nav_output = ""
    for nav_link in header_links:
        url = nav_link.get("url", "")
        title = html_escape(nav_link.get("title", ""))
        link = tk.literal('<a href="{}">{}</a>'.format(url, title))
        if url.endswith(tk.request.path):
            li = tk.literal('<li class="active">') + link + tk.literal("</li>")
        else:
            li = tk.literal("<li>") + link + tk.literal("</li>")
        nav_output = nav_output + li
    return nav_output


def get_header_layout():
    controller = CustomHeaderController()
    custom_header = controller.get_custom_header_metadata()
    layout_type = custom_header.get("layout_type", "default")
    return layout_type


def custom_header_validator(value):
    if value.get("layout_type") not in ["compressed", "default"]:
        raise tk.Invalid("Header layout is not supported")
    for item in value.get("links", []):
        title = item.get("title", "")
        custom_header_title_validator(title)
        url = item.get("url", "")
        custom_header_url_validator(url)
    return value


@helper.value_should_be_not_empty("URL")
@helper.value_should_be_shorter_than_length("URL", 2000)
def custom_header_url_validator(url):
    def check_characters(value):
        if set(value) <= set(string.ascii_letters + string.digits + "-./"):
            return False
        return True

    pieces = urlparse(url)
    if pieces.scheme and pieces.scheme != "https":
        raise tk.Invalid('Only HTTPS URLs supported "{}"'.format(url))
    elif not pieces.path and not all([pieces.scheme, pieces.netloc]):
        raise tk.Invalid("Empty relative path in relative url {}".format(url))
    elif (
        pieces.path
        and not all([pieces.scheme, pieces.netloc])
        and check_characters(pieces.path)
    ):
        raise tk.Invalid("Relative path contains invalid characters {}".format(url))
    elif pieces.netloc and check_characters(pieces.netloc):
        raise tk.Invalid('URL contains invalid characters "{}"'.format(url))
    tk.h.render_markdown
    return url


@helper.value_should_be_not_empty(field_name="title")
@helper.value_should_be_shorter_than_length(field_name="Title", length=50)
def custom_header_title_validator(title):
    cleaned_title = helper.sanityze_all_html(title)
    return cleaned_title
