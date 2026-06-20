import logging

from flask import Blueprint, make_response, redirect, url_for, request
import ckanext.pose_theme.custom_themes.pose_theme.utils as utils

log = logging.getLogger(__name__)

datastore_dictionary = Blueprint(u'datastore_dictionary', __name__)


def dictionary_download(resource_id):
    response = make_response()
    response.headers[u'content-type'] = u'application/octet-stream'
    return utils.dictionary_download(resource_id, response)


datastore_dictionary.add_url_rule(u'/datastore/dictionary_download/<resource_id>', view_func=dictionary_download)


@datastore_dictionary.before_app_request
def allow_tool_finish_without_resources():
    """
    CKAN requires at least one resource when finishing dataset creation.
    For the 'tool' type, resources are optional — intercept the resource
    creation POST before CKAN's view runs and activate the dataset directly.
    """
    if request.endpoint != u'tool_resource.new' or request.method != u'POST':
        return
    save_action = request.form.get(u'save')
    if save_action in (u'again', u'go-dataset', u'go-dataset-complete'):
        return
    has_url = bool(request.form.get(u'url', u'').strip())
    has_upload = bool(request.files.get(u'upload'))
    if has_url or has_upload:
        return

    # No resource data — activate the dataset and redirect to its page
    try:
        from ckan.plugins.toolkit import h, get_action, ObjectNotFound, NotAuthorized, ValidationError
        import ckan.model as model
        from ckan.common import current_user
        pkg_id = request.view_args.get(u'id')
        context = {
            u'model': model,
            u'session': model.Session,
            u'user': current_user.name,
            u'auth_user_obj': current_user,
        }
        data_dict = get_action(u'package_show')(context, {u'id': pkg_id})
        get_action(u'package_update')(
            dict(context, allow_state_change=True),
            dict(data_dict, state=u'active')
        )
        return h.redirect_to(u'tool.read', id=data_dict[u'name'])
    except (ObjectNotFound, NotAuthorized, ValidationError):
        return  # fall through to CKAN's normal handling
    except Exception:
        log.exception(u'Unexpected error in allow_tool_finish_without_resources')
        return  # fall through to CKAN's normal handling


@datastore_dictionary.before_app_request
def redirect_dataset_to_typed_url():
    """
    Redirect /dataset/<id> to the correct type-specific URL (301) when the
    package is not a plain 'dataset' type. Prevents duplicate-content issues
    for site/extension/tool/showcase packages.
    """
    if request.endpoint != u'dataset.read' or request.method != u'GET':
        return
    pkg_id = (request.view_args or {}).get(u'id')
    if not pkg_id:
        return
    try:
        from ckan.plugins.toolkit import get_action
        pkg = get_action(u'package_show')({}, {u'id': pkg_id})
        pkg_type = pkg.get(u'type', u'dataset')
        if pkg_type != u'dataset':
            return redirect(url_for(u'{}.read'.format(pkg_type), id=pkg[u'name']), 301)
    except Exception:
        return


# Discourse SSO / topic-creation POSTs back to the originating page URL.
# The scheming read routes only accept GET, so redirect POST → GET.
discourse_post_compat = Blueprint(u'discourse_post_compat', __name__)


@discourse_post_compat.route(u'/site/<id>', methods=[u'POST'])
def site_read_post(id):
    return redirect(url_for(u'site.read', id=id), 303)


@discourse_post_compat.route(u'/extension/<id>', methods=[u'POST'])
def extension_read_post(id):
    return redirect(url_for(u'extension.read', id=id), 303)


def get_blueprints():
    return [datastore_dictionary, discourse_post_compat]
 