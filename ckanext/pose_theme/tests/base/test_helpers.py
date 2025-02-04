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
