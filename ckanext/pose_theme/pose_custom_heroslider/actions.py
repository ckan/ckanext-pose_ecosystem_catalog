import datetime
import json
import logging

import ckan.lib.uploader as uploader
import ckan.lib.helpers as h
import ckan.plugins.toolkit as toolkit
import ckan.lib.navl.dictization_functions as dict_fns
from ckan import model

from ckanext.pose_theme.pose_custom_heroslider import db

unicode_safe = toolkit.get_validator('unicode_safe')


ignore_empty = toolkit.get_validator('ignore_empty')
ignore_missing = toolkit.get_validator('ignore_missing')
not_empty = toolkit.get_validator('not_empty')
isodate = toolkit.get_validator('isodate')

log = logging.getLogger(__name__)


hero_slider_schema = {
    'id': [ignore_empty, unicode_safe],
    'image_url_1': [ignore_empty, unicode_safe],
    'hero_text_1': [ignore_empty, unicode_safe],
    'image_url_2': [ignore_empty, unicode_safe],
    'hero_text_2': [ignore_empty, unicode_safe],
    'image_url_3': [ignore_empty, unicode_safe],
    'hero_text_3': [ignore_empty, unicode_safe],
    'image_url_4': [ignore_empty, unicode_safe],
    'hero_text_4': [ignore_empty, unicode_safe],
    'image_url_5': [ignore_empty, unicode_safe],
    'hero_text_5': [ignore_empty, unicode_safe],
    'created': [ignore_missing, isodate],
    'modified': [ignore_missing, isodate]
}


def hero_slider_update(context, data_dict):
    session = context['session']

    toolkit.check_access('hero_slider_update', context, data_dict)

    # validate the incoming data_dict
    validated_data_dict, errors = dict_fns.validate(
        data_dict, hero_slider_schema, context
    )

    if errors:
        raise toolkit.ValidationError(errors)

    hero = db.Hero_Slider.get_hero_images()
    if not hero:
        hero = db.Hero_Slider()

    for i in range(1,6):
        field_url = 'image_url_{}'.format(i)
        setattr(hero, field_url, data_dict.get(field_url))

        hero_text = 'hero_text_{}'.format(i)
        setattr(hero, hero_text, data_dict.get(hero_text))

    hero.modified = datetime.datetime.utcnow()

    hero.save()
    session.add(hero)
    session.commit()

    return hero


@toolkit.side_effect_free
def hero_slider_list(context, data_dict):
    hero = db.Hero_Slider.get_hero_images()
    if hero:
        hero = db.table_dictize(hero, context)

        for i in range(1,6):
            field_url = 'image_url_{}'.format(i)
            image_display_url = 'image_display_url_{}'.format(i)

            image_url = hero.get(field_url)
            if not image_url:
                continue

            if image_url.startswith('http'):
                hero[image_display_url] = image_url
            else:
                if not image_url.startswith('/uploads'):
                    image_url = '/uploads/hero/{}'.format(image_url)
                hero[image_display_url] = h.url_for_static(
                    image_url,
                    qualified=True
                )

    return hero
