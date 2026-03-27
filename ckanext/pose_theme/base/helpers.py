import ast
import bleach
import json
import logging
import re
import string
import threading
import time
from datetime import datetime, timezone

import ckan.model as model

from ckan.plugins import toolkit
from ckan.plugins.toolkit import config
from packaging.version import Version

from ckanext.pose_theme.base.compatibility_controller import BaseCompatibilityController
from ckanext.pose_theme.pose_custom_homepage.constants import CUSTOM_NAMING


logger = logging.getLogger(__name__)


def dataset_count():
    """Return a count of all datasets"""
    count = 0
    try:
        result = toolkit.get_action('package_search')({}, {'rows': 1})
        if result.get('count'):
            count = result.get('count')
    except Exception:
        logger.debug("[pose_theme] Error getting dataset count")
        return 0
    return count


def showcases(num=12):
    """Return a list of showcases"""
    sorted_showcases = []
    try:
        showcases = toolkit.get_action('ckanext_showcase_list')({}, {})
        sorted_showcases = sorted(showcases, key=lambda k: k.get('metadata_modified'), reverse=True)
    except Exception:
        logger.debug("[pose_theme] Error getting showcase list")
        return []
    return sorted_showcases[:num]


def extensions(num=24):
    """Return a list of extensions"""
    sorted_extensions = []
    try:
        extensions = toolkit.get_action('ckanext_extensions_list')({}, {})
        sorted_extensions = sorted(extensions, key=lambda k: k.get('metadata_modified'), reverse=True)
    except Exception:
        logger.debug("[pose_theme] Error getting extensions list")
        return []
    return sorted_extensions[:num]

def sites(num=24):
    """Return a list of sites"""
    sorted_sites = []
    try:
        sites = toolkit.get_action('ckanext_sites_list')({}, {})
        sorted_sites = sorted(sites, key=lambda k: k.get('metadata_modified'), reverse=True)
    except Exception:
        logger.debug("[pose_theme] Error getting sites list")
        return []
    return sorted_sites[:num]


def groups(num=12):
    """Return a list of groups"""
    groups = []
    try:
        groups = toolkit.get_action('group_list')({}, {'all_fields': True, 'sort': 'packages'})
    except Exception:
        logger.debug("[pose_theme] Error getting group list")
        return []
    return groups[:num]


def organization(num=12):
    """Return a list of groups"""
    groups = []
    try:
        groups = toolkit.get_action('organization_list')({}, {'all_fields': True, 'sort': 'packages'})
    except Exception:
        logger.debug("[pose_theme] Error getting organization list")
        return []
    return groups[:num]


def popular_datasets(num=6):
    """Return a list of popular datasets."""
    datasets = []
    try:
        search = toolkit.get_action('package_search')({}, {'rows': num, 'sort': 'views_recent desc'})
        if search.get('results'):
            datasets = search.get('results')
    except Exception:
        logger.debug("[pose_theme] Error getting popular datasets")
        return []
    return datasets[:num]


def recent_datasets(num=6):
    """Return a list of recently updated/created datasets."""
    sorted_datasets = []
    try:
        datasets = toolkit.get_action('current_package_list_with_resources')({}, {'limit': num})
        if datasets:
            sorted_datasets = sorted(datasets, key=lambda k: k['metadata_modified'], reverse=True)
    except Exception:
        logger.debug("[pose_theme] Error getting recently updated/created datasets")
        return []
    return sorted_datasets[:num]

def featured_extensions(num=6):
    """Return featured extension datasets """
    featured_extensions_list = []
    try:
        # Use package_search to filter for extensions and sort by stars (descending)
        search_result = toolkit.get_action('package_search')({}, {
            'q': 'type:extension',
            'fq': 'extras_is_featured:TRUE',
            'rows': num,
            'start': 0
        })
        
        if search_result and 'results' in search_result:
            featured_extensions_list = search_result['results']
    except Exception as e:
        logger.error(f"[pose_theme] Error getting popular extensions: {str(e)}", exc_info=True)
        
        return []
        
    
    return featured_extensions_list[:num]

def featured_sites(num=6):
    """Return featured extension datasets """
    featured_site_list = []
    try:
        # Use package_search to filter for extensions and sort by stars (descending)
        search_result = toolkit.get_action('package_search')({}, {
            'q': 'type:site',
            'fq': 'extras_is_featured:TRUE',
            'rows': num,
            'start': 0
        })
        
        if search_result and 'results' in search_result:
            featured_site_list = search_result['results']
    except Exception as e:
        logger.error(f"[pose_theme] Error getting popular site: {str(e)}", exc_info=True)
        
        return []
        
    
    return featured_site_list[:num]  

def site_of_month():
    """Return the site designated as Site of the Month for the current month."""
    current_month = datetime.utcnow().strftime('%Y-%m')
    try:
        search_result = toolkit.get_action('package_search')({}, {
            'q': 'type:site',
            'fq': f'extras_sotm_month:{current_month}',
            'rows': 1,
            'start': 0
        })
        if search_result and search_result.get('results'):
            return search_result['results'][0]
    except Exception as e:
        logger.error(f"[pose_theme] Error getting site of the month: {str(e)}", exc_info=True)
    return None


def recent_extensions(num=6):
    """Return a list of recently updated/created extension datasets."""
    sorted_extensions = []
    try:
        # Use package_search to filter for extensions and sort by metadata_modified
        search_result = toolkit.get_action('package_search')({}, {
            'q': 'type:extension',
            'sort': 'metadata_modified desc',
            'rows': num,
            'start': 0
        })

        if search_result and 'results' in search_result:
            sorted_extensions = search_result['results']
    except Exception:
        logger.debug("[pose_theme] Error getting recently updated/created extensions")
        return []

    return sorted_extensions[:num]


def tools(num=24):
    """Return a list of tools."""
    sorted_tools = []
    try:
        search_result = toolkit.get_action('package_search')({}, {
            'q': 'type:tool',
            'sort': 'metadata_modified desc',
            'rows': num,
            'start': 0
        })
        if search_result and 'results' in search_result:
            sorted_tools = search_result['results']
    except Exception:
        logger.debug("[pose_theme] Error getting tool list")
        return []
    return sorted_tools[:num]


def featured_tools(num=6):
    """Return featured tool datasets."""
    featured_tools_list = []
    try:
        search_result = toolkit.get_action('package_search')({}, {
            'q': 'type:tool',
            'fq': 'extras_is_featured:TRUE',
            'rows': num,
            'start': 0
        })
        if search_result and 'results' in search_result:
            featured_tools_list = search_result['results']
    except Exception as e:
        logger.error(f"[pose_theme] Error getting featured tools: {str(e)}", exc_info=True)
        return []
    return featured_tools_list[:num]


def recent_tools(num=6):
    """Return a list of recently updated/created tool datasets."""
    sorted_tools = []
    try:
        search_result = toolkit.get_action('package_search')({}, {
            'q': 'type:tool',
            'sort': 'metadata_modified desc',
            'rows': num,
            'start': 0
        })
        if search_result and 'results' in search_result:
            sorted_tools = search_result['results']
    except Exception:
        logger.debug("[pose_theme] Error getting recently updated/created tools")
        return []
    return sorted_tools[:num]



def new_datasets(num=3):
    """Return a list of the newly created datasets."""
    datasets = []
    try:
        search = toolkit.get_action('package_search')({}, {'rows': num, 'sort': 'metadata_created desc'})
        if search.get('results'):
            datasets = search.get('results')
    except Exception:
        logger.debug("[pose_theme] Error getting newly created datasets")
        return []
    return datasets[:num]


def get_user_uuid():
    """Return the user platform_uuid for a given email, if there is a token for that email"""
    if toolkit.g.user:
        user = toolkit.g.userobj
        try:
            user_token = model.Session.query(model.UserToken).filter(model.UserToken.email == user.email).first()
            if user_token:
                return user_token.platform_uuid
            return None
        except Exception as e:
            logger.debug("[opendata_theme] Error querying user token: {}".format(e))
            return None
    return None


def package_tracking_summary(package):
    """Return the tracking summary of a dataset"""
    tracking_summary = {}
    try:
        result = toolkit.get_action('package_show')({}, {'id': package.get('name'), 'include_tracking': True})
        if result.get('tracking_summary'):
            tracking_summary = result.get('tracking_summary')
    except Exception:
        logger.debug("[pose_theme] Error getting dataset tracking_summary")
        return {}
    return tracking_summary


def is_data_dict_active(ddict):
    """"Returns True if data dictionary is populated"""
    for col in ddict:
        info = col.get('info', {})
        if info.get('label') or info.get('notes'):
            return True
    return False


def get_group_alias():
    return str(config.get('ckan.group_alias', 'Group'))


def get_organization_alias():
    return str(config.get('ckan.organization_alias', 'Organization'))


def get_custom_name(key, default_name):
    custom_naming = toolkit.get_action('config_option_show')({'ignore_auth': True}, {"key": CUSTOM_NAMING})
    if not custom_naming:
        return default_name
    custom_naming = ast.literal_eval(custom_naming)
    name = custom_naming.get(key)
    if not name:
        return default_name
    else:
        return toolkit.h.markdown_extract(name.get('value', default_name))


def get_data(key):
    return BaseCompatibilityController.get_data(key)


def version_builder(text_version):
    return Version(text_version)


def get_story_banner():
    """Return a showcase with a specific story tag"""
    existent_showcases = showcases()
    for showcase in existent_showcases:
        for tag in showcase['tags']:
            if tag['name'].lower() in ['story banner', 'story-banner', 'story+banner']:
                return showcase


def showcase_story(story=True, num=12):
    """Return list of Showcase whose tag is story"""

    existent_showcases = showcases()
    sorted_tags = {}
    std_story_showcase = []
    for showcase in existent_showcases:
        for tag in showcase['tags']:
            if tag['name'].lower() == 'story':
                std_story_showcase.append(showcase)
                continue

            story_tag = re.findall("story[ +-]?[0-9]+$", tag['name'])

            if len(story_tag) > 0:
                key = re.findall(r'\d+', story_tag[0])
                if int(key[0]) in sorted_tags:
                    temp = sorted_tags[int(key[0])]
                    temp.append(showcase)
                    sorted_tags[int(key[0])] = temp
                else:
                    temp = []
                    temp.append(showcase)
                    sorted_tags[int(key[0])] = temp

    dict_keys_sorted = sorted(list(sorted_tags))

    sorted_showcases = []
    for key in dict_keys_sorted:
        showcases_tags_num = sorted_tags.get(key)
        for showcase in showcases_tags_num:
            sorted_showcases.append(showcase)
    for showcase in std_story_showcase:
        if showcase not in sorted_showcases:
            sorted_showcases.append(showcase)

    if story is False:
        default_showcases = []
        for showcase in existent_showcases:
            if showcase not in sorted_showcases:
                default_showcases.append(showcase)
        return default_showcases
    else:
        return sorted_showcases


def get_value_from_extras(extras, key):
    value = ''
    for item in extras:
        if item.get('key') == key:
            value = item.get('value')
    return value


def search_document_page_exists(page_id):
    try:
        if not page_id:
            return False
        search_doc = toolkit.get_action('ckanext_pages_show')({}, {'page': page_id})
        if search_doc.get('content') and not search_doc.get('private'):
            return True
    except Exception:
        logger.debug("[pose_theme] Error in retrieving page")
    return False


def check_characters(value):
    if value in ['', None]:
        return False
    if value and set(value) <= set(string.printable):
        return False
    return True


def sanityze_all_html(text):
    cleaned_text = bleach.clean(text, tags=[], attributes={})
    return cleaned_text


def value_should_be_not_empty(field_name='text'):
    def decorator(func):
        def _wrap(value):
            if not value:
                raise toolkit.Invalid('Missing {}'.format(field_name))
            return func(value)
        return _wrap
    return decorator


def value_should_be_shorter_than_length(field_name='Field', length=30):
    def decorator(func):
        def _wrap(value):
            if len(value) > length:
                raise toolkit.Invalid(
                    '{} is too long. Maximum {} characters allowed for {}'.format(field_name, length, value)
                )
            return func(value)
        return _wrap
    return decorator


def get_default_extent():
    """
    Return default extent to use with spatial widget
    If none is configured a bounding box of the continental US is returned
    """
    return config.get(
        'ckanext.spatial.default_extent',
        '{ "type": "Polygon", \
           "coordinates": [[[-124.7844079,24.7433195], \
            [-66.9513812,24.7433195],[-66.9513812,49.3457868], \
            [-124.7844079,49.3457868],[-124.7844079,24.7433195]]] }'
    )


def get_column_count():
    return int(config.get('ckanext.pose_theme.column_count', 4))


def is_activity_enabled():
    return 'activity' in config.get('ckan.plugins', '')

def get_maptiler_api_key():
   return config.get('ckanext.pose_theme.maptiler_api_key', '')


def get_discourse_url():
    url = (
        config.get('ckanext.pose_theme.discourse_url')
        or config.get('discourse.url')
        or 'https://community.civicdataecosystem.org'
    )
    return url.rstrip('/')


_discourse_cache = {'topics': None, 'expires': 0}
_discourse_cache_lock = threading.Lock()
_DISCOURSE_CACHE_TTL = 300  # seconds


def discourse_latest_topics(num=6):
    """Fetch the latest non-pinned topics from the configured Discourse forum.

    Results are cached in-memory for _DISCOURSE_CACHE_TTL seconds to avoid
    hammering the Discourse API on every homepage request.
    """
    global _discourse_cache
    from urllib.request import urlopen, Request

    now = time.time()
    if _discourse_cache['topics'] is not None and now < _discourse_cache['expires']:
        return _discourse_cache['topics'][:num]

    def _relative_time(date_str):
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            _now = datetime.now(timezone.utc)
            diff = int((_now - dt).total_seconds())
            if diff < 60:
                return 'just now'
            if diff < 3600:
                return '{}m ago'.format(diff // 60)
            if diff < 86400:
                return '{}h ago'.format(diff // 3600)
            if diff < 2592000:
                return '{}d ago'.format(diff // 86400)
            return '{}mo ago'.format(diff // 2592000)
        except Exception:
            return ''

    with _discourse_cache_lock:
        # Re-check inside the lock — another thread may have just refreshed
        if _discourse_cache['topics'] is not None and now < _discourse_cache['expires']:
            return _discourse_cache['topics'][:num]

        forum_url = get_discourse_url()
        try:
            req = Request(
                forum_url + '/latest.json',
                headers={'Accept': 'application/json', 'User-Agent': 'CKAN-pose-ecosystem-catalog/1.0'},
            )
            with urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))

            # Build a username → avatar_url lookup from the top-level users list
            user_avatars = {}
            for u in data.get('users', []):
                template = u.get('avatar_template', '')
                if template:
                    avatar_url = template.replace('{size}', '40')
                    if avatar_url.startswith('/'):
                        avatar_url = forum_url + avatar_url
                    user_avatars[u['username']] = avatar_url

            raw = data.get('topic_list', {}).get('topics', [])
            topics = []
            for t in raw:
                if t.get('pinned'):
                    continue
                last_posted = t.get('last_posted_at') or t.get('created_at', '')
                username = t.get('last_poster_username', '')
                topics.append({
                    'title': t.get('title', ''),
                    'url': '{}/t/{}/{}'.format(forum_url, t.get('slug', ''), t.get('id', '')),
                    'reply_count': max(t.get('posts_count', 1) - 1, 0),
                    'relative_time': _relative_time(last_posted),
                    'last_poster': username,
                    'avatar_url': user_avatars.get(username, ''),
                    'excerpt': t.get('excerpt', '').split('\n')[0][:120].strip(),
                })
                if len(topics) >= 20:  # cap fetch; cache the full set
                    break
            _discourse_cache = {'topics': topics, 'expires': now + _DISCOURSE_CACHE_TTL}
            return topics[:num]
        except Exception as e:
            logger.debug("[pose_theme] Error fetching Discourse topics: %s", e)
            return _discourse_cache['topics'][:num] if _discourse_cache['topics'] else []


EXCLUDED_EDITORS = {'ckan_bot', 'a5dur'}


def get_latest_editor(package_id):
    """Return info about the most recent human editor of a package, skipping bot users."""
    try:
        activities = toolkit.get_action('package_activity_list')(
            {'ignore_auth': True},
            {'id': package_id, 'limit': 25}
        )
        for activity in activities:
            user_id = activity.get('user_id')
            if not user_id:
                continue
            user = toolkit.get_action('user_show')(
                {'ignore_auth': True},
                {'id': user_id, 'include_datasets': False}
            )
            if user.get('name') in EXCLUDED_EDITORS:
                continue
            return {
                'name': user.get('display_name') or user.get('fullname') or user.get('name'),
                'username': user.get('name'),
                'timestamp': activity.get('timestamp'),
                'activity_type': activity.get('activity_type', ''),
            }
    except Exception:
        logger.debug("[pose_theme] Error getting latest editor for package %s", package_id)
    return None
