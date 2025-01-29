import six
from ckan.lib.helpers import url_for
from ckan.tests import factories


def get_env(is_sysadmin):
    sysadmin = factories.Sysadmin() if is_sysadmin else factories.User()
    return {"REMOTE_USER": six.ensure_str(sysadmin["name"])}


def do_get(app, path, is_sysadmin=True):
    env = get_env(is_sysadmin)
    url = url_for(path)
    return app.get(url=url, extra_environ=env)


def do_post(app, path, data, is_sysadmin=True):
    env = get_env(is_sysadmin)
    url = url_for(path)
    return app.post(url=url, extra_environ=env, data=data)
