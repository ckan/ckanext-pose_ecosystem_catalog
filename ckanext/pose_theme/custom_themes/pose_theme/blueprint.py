from flask import Blueprint, make_response, request
import ckanext.pose_theme.custom_themes.pose_theme.utils as utils

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
        from ckan.plugins.toolkit import h, get_action, abort, _
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
    except Exception:
        return  # fall through to CKAN's normal handling


def get_blueprints():
    return [datastore_dictionary]
 