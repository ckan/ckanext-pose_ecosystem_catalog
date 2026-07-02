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


# Serve dataset-resource thumbnails under a static-looking /assets/thumbnails/
# path instead of /dataset/<id>/resource/<id>/download/<file>. The homepage
# thumbnails are dataset resources; on the /dataset/* path Cloudflare's bot
# challenge gates them so they don't load until the visitor is verified.
# /assets/* is covered by the static-asset cache rule (no challenge), so the
# images load immediately. This is a URL alias — it streams/redirects to the
# live resource, so there's no file duplication and it works for both local
# and S3 (s3filestore) storage.
thumbnails = Blueprint(u'pose_thumbnails', __name__)


@thumbnails.route(u'/assets/thumbnails/<resource_id>')
def thumbnail(resource_id):
    from ckan.plugins.toolkit import abort, get_action, ObjectNotFound, NotAuthorized
    from ckan.common import current_user
    from flask import current_app
    import ckan.model as model

    # Use the real request user so authorized viewers of private packages are
    # not falsely 404'd by an anonymous ({}) context.
    context = {
        u'model': model,
        u'session': model.Session,
        u'user': current_user.name,
        u'auth_user_obj': current_user,
    }
    try:
        resource = get_action(u'resource_show')(context, {u'id': resource_id})
        # This alias is only for uploaded thumbnails; reject link/datastore
        # resources so it can't be used to redirect to arbitrary URLs.
        if resource.get(u'url_type') != u'upload':
            return abort(404)
        pkg = get_action(u'package_show')(context, {u'id': resource[u'package_id']})
    except (ObjectNotFound, NotAuthorized):
        return abort(404)

    # Delegate to whichever resource-download view is actually registered so
    # the active filestore serves the file. ckanext-s3filestore overrides the
    # download route (endpoint 's3_resource.resource_download') to stream from
    # S3; importing ckan.views.resource.download directly would bypass that and
    # read from local disk, which fails when files live on S3.
    pkg_type = pkg.get(u'type', u'dataset')
    view = (current_app.view_functions.get(u's3_resource.resource_download')
            or current_app.view_functions.get(u'{}_resource.download'.format(pkg_type))
            or current_app.view_functions.get(u'resource.download'))
    return view(
        package_type=pkg_type,
        id=pkg[u'id'],
        resource_id=resource_id,
    )


def get_blueprints():
    return [datastore_dictionary, discourse_post_compat, thumbnails]
 