# encoding: utf-8
import ckan.plugins.toolkit as toolkit

try:
    from ckan.common import config  # CKAN 2.7 and later
except ImportError:
    from pylons import config  # CKAN 2.7 and earlier


def dataset_count():
    """Return a count of all datasets"""
    count = 0
    result = toolkit.get_action("package_search")({}, {"rows": 1})
    if result.get("count"):
        count = result.get("count")
    return count


def get_hero_images():
    image_list = []
    result = toolkit.get_action("hero_slider_list")({}, {})
    if result:
        for i in range(1, 6):
            field_name = "image_{}".format(i)
            image_display_url = result.get("image_display_url_{}".format(i))
            image_list.append({field_name: image_display_url})

    if not image_list:
        image_list.append({"image_1": "/assets/background_BixbyCreekBridge.jpg"})
        image_list.append({"image_2": "/assets/background_SardineLake.jpg"})

    return image_list


def get_hero_text(field_name):
    hero_dict = {}
    result = toolkit.get_action("hero_slider_list")({}, {})
    if result:
        for i in range(1, 6):
            field_url = "image_url_{}".format(i)
            hero_text = "hero_text_{}".format(i)

            if field_name in [field_url, hero_text]:
                hero_dict["hero_text"] = result.get(hero_text)
    return hero_dict


def get_max_image_size():
    max_image_size = int(config.get("ckan.max_image_size", 2))
    return max_image_size
