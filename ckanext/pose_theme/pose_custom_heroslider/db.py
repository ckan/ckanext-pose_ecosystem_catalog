import datetime
import uuid
import json

from six import text_type
import sqlalchemy as sa
from sqlalchemy.orm import class_mapper

from sqlalchemy.engine.result import Row

import ckan.model as model


hero_slider_table = None


def _make_uuid():
    return text_type(uuid.uuid4())


def init():
    if hero_slider_table is None:
        define_hero_slider_table()

    if not hero_slider_table.exists():
        hero_slider_table.create()


class Hero_Slider(model.DomainObject):

    @classmethod
    def get_hero_images(self):
        query = model.Session.query(self).autoflush(False)
        return query.first()


def define_hero_slider_table():
    global hero_slider_table
    hero_slider_table = sa.Table(
        "hero_slider",
        model.meta.metadata,
        sa.Column("id", sa.types.UnicodeText, primary_key=True, default=_make_uuid),
        sa.Column("image_url_1", sa.types.UnicodeText, default=""),
        sa.Column("hero_text_1", sa.types.UnicodeText, default=""),
        sa.Column("image_url_2", sa.types.UnicodeText, default=""),
        sa.Column("hero_text_2", sa.types.UnicodeText, default=""),
        sa.Column("image_url_3", sa.types.UnicodeText, default=""),
        sa.Column("hero_text_3", sa.types.UnicodeText, default=""),
        sa.Column("image_url_4", sa.types.UnicodeText, default=""),
        sa.Column("hero_text_4", sa.types.UnicodeText, default=""),
        sa.Column("image_url_5", sa.types.UnicodeText, default=""),
        sa.Column("hero_text_5", sa.types.UnicodeText, default=""),
        sa.Column("created", sa.types.DateTime, default=datetime.datetime.now),
        sa.Column("modified", sa.types.DateTime, default=datetime.datetime.now),
        extend_existing=True,
    )

    model.meta.mapper(Hero_Slider, hero_slider_table)


def table_dictize(obj, context, **kw):
    """Get any model object and represent it as a dict"""
    result_dict = {}

    if isinstance(obj, Row):
        fields = obj.keys()
    else:
        ModelClass = obj.__class__
        table = class_mapper(ModelClass).mapped_table
        fields = [field.name for field in table.c]

    for field in fields:
        name = field
        if name in ("current", "expired_timestamp", "expired_id"):
            continue
        if name == "continuity_id":
            continue
        value = getattr(obj, name)
        if name == "extras" and value:
            result_dict.update(json.loads(value))
        elif value is None:
            result_dict[name] = value
        elif isinstance(value, dict):
            result_dict[name] = value
        elif isinstance(value, int):
            result_dict[name] = value
        elif isinstance(value, datetime.datetime):
            result_dict[name] = value.isoformat()
        elif isinstance(value, list):
            result_dict[name] = value
        else:
            result_dict[name] = text_type(value)

    result_dict.update(kw)

    ##HACK For optimisation to get metadata_modified created faster.

    context["metadata_modified"] = max(
        result_dict.get("revision_timestamp", ""), context.get("metadata_modified", "")
    )

    return result_dict
