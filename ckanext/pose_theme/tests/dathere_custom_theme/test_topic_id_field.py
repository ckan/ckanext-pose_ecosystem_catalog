"""topic_id must be appended to the dataset schema exactly once."""
from ckanext.pose_theme.custom_themes.pose_theme.plugin import (
    add_topic_id_field)


def _names(schema):
    return [f['field_name'] for f in schema['dataset_fields']]


def test_appends_when_missing():
    schema = {'dataset_fields': [{'field_name': 'title'}]}
    assert _names(add_topic_id_field(schema)) == ['title', 'topic_id']


def test_is_idempotent():
    schema = {'dataset_fields': [{'field_name': 'title'}]}
    add_topic_id_field(schema)
    add_topic_id_field(schema)
    assert _names(schema).count('topic_id') == 1


def test_leaves_declared_field_alone():
    schema = {'dataset_fields': [
        {'field_name': 'topic_id', 'label': 'Topic ID', 'form_snippet': None}]}
    add_topic_id_field(schema)
    assert len(schema['dataset_fields']) == 1
