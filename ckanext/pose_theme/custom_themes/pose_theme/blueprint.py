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


_OPTIONAL_RESOURCE_TYPES = {
    u'tool_resource': u'tool',
    u'site_resource': u'site',
    u'extension_resource': u'extension',
}


@datastore_dictionary.before_app_request
def allow_finish_without_resources():
    """
    Resources are optional for tool/site/extension types.
    Intercept the resource-creation POST and activate the dataset directly
    when no resource data is provided.
    """
    pkg_type = _OPTIONAL_RESOURCE_TYPES.get(
        request.endpoint.rsplit(u'.', 1)[0] if request.endpoint else u''
    )
    if not pkg_type or request.method != u'POST':
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
        return h.redirect_to(u'{}.read'.format(pkg_type), id=data_dict[u'name'])
    except (ObjectNotFound, NotAuthorized, ValidationError):
        return  # fall through to CKAN's normal handling
    except Exception:
        log.exception(u'Unexpected error in allow_finish_without_resources')
        return  # fall through to CKAN's normal handling


# Discourse SSO / topic-creation POSTs back to the originating page URL.
# The scheming read routes only accept GET, so redirect POST → GET.
discourse_post_compat = Blueprint(u'discourse_post_compat', __name__)


@discourse_post_compat.route(u'/site/<id>', methods=[u'POST'])
def site_read_post(id):
    if id == u'new':
        from flask import current_app
        return current_app.view_functions[u'site.new'](package_type=u'site')
    return redirect(url_for(u'site.read', id=id), 303)


@discourse_post_compat.route(u'/extension/<id>', methods=[u'POST'])
def extension_read_post(id):
    if id == u'new':
        from flask import current_app
        return current_app.view_functions[u'extension.new'](package_type=u'extension')
    return redirect(url_for(u'extension.read', id=id), 303)


def get_blueprints():
    return [datastore_dictionary, discourse_post_compat]
 