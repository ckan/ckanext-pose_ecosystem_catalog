import pytest

from ckanext.pose_theme.base.helpers import version_builder
from packaging.version import InvalidVersion


def test_version_builder_positive():
    assert version_builder('2.7') < version_builder('2.9')
    assert version_builder('2.7.0') < version_builder('2.7.3')
    assert version_builder('2.7.3') < version_builder('2.7.12')
    assert version_builder('2.7.3') < version_builder('2.9.0')
    assert version_builder('2.7.3') < version_builder('2.9.7')
    assert version_builder('2.7.12') < version_builder('2.9.0')
    assert version_builder('2.7.12') < version_builder('2.9.7')
    assert version_builder('2.7.12') < version_builder('2.10.0')


def test_version_builder_failed_to_build():
    with pytest.raises(InvalidVersion):
        assert version_builder('1.3.xy123')


def _res(**kw):
    return dict({'id': 'r', 'url': '', 'format': '', 'url_type': None}, **kw)


def test_pick_screenshot_prefers_flagged_resource():
    from ckanext.pose_theme.base.helpers import _pick_screenshot
    first = _res(id='a', format='PNG', url='http://x/a.png')
    flagged = _res(id='b', format='JPEG', url='http://x/b.jpg', is_screenshot='true')
    assert _pick_screenshot([first, flagged]) is flagged


def test_pick_screenshot_falls_back_to_first_image():
    from ckanext.pose_theme.base.helpers import _pick_screenshot
    page = _res(id='a', format='HTML', url='http://x/page')
    image = _res(id='b', format='', url='http://x/b.png?v=1')
    assert _pick_screenshot([page, image]) is image


def test_pick_screenshot_ignores_non_image_resources():
    from ckanext.pose_theme.base.helpers import _pick_screenshot
    assert _pick_screenshot([_res(format='HTML', url='http://x/page')]) is None


def test_pick_screenshot_keeps_first_resource_without_formats():
    from ckanext.pose_theme.base.helpers import _pick_screenshot
    shot = _res(id='a', url='http://x/shot')
    assert _pick_screenshot([shot]) is shot


def test_resource_optional_hook_only_matches_new_endpoint():
    from ckanext.pose_theme.custom_themes.pose_theme.blueprint import _OPTIONAL_RESOURCE_TYPES
    assert set(_OPTIONAL_RESOURCE_TYPES) == {
        'site_resource.new', 'tool_resource.new', 'extension_resource.new'}
