import ckan.plugins.toolkit as tk


def hero_slider_update(context, data_dict):
    return {'success':  False}


@tk.auth_allow_anonymous_access
def hero_slider_list(context, data_dict):
    return {'success': True}
