from types import SimpleNamespace

from ckanext.pose_theme.custom_themes.pose_theme.blueprint import (
    S3_DOWNLOAD_ENDPOINT,
    route_typed_downloads_to_filestore,
)


def _core_download():
    pass


def _s3_download():
    pass


def _app(**views):
    return SimpleNamespace(view_functions=dict(views))


def test_typed_downloads_go_to_s3filestore():
    app = _app(**{
        S3_DOWNLOAD_ENDPOINT: _s3_download,
        'resource.download': _core_download,
        'site_resource.download': _core_download,
        'extension_resource.download': _core_download,
        'site_resource.read': _core_download,
    })
    assert route_typed_downloads_to_filestore(app) == [
        'extension_resource.download', 'site_resource.download']
    views = app.view_functions
    assert views['site_resource.download'] is _s3_download
    assert views['extension_resource.download'] is _s3_download
    assert views['resource.download'] is _core_download
    assert views['site_resource.read'] is _core_download


def test_without_s3filestore_nothing_changes():
    app = _app(**{'site_resource.download': _core_download})
    assert route_typed_downloads_to_filestore(app) == []
    assert app.view_functions['site_resource.download'] is _core_download


def test_wrapped_wsgi_app_is_left_alone():
    assert route_typed_downloads_to_filestore(object()) == []
