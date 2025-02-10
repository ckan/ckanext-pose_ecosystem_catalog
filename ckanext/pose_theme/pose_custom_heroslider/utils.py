# encoding: utf-8
import logging

import ckan.plugins.toolkit as tk
import ckan.lib.helpers as h
import ckan.lib.uploader as uploader
import ckan.lib.navl.dictization_functions as dict_fns
import ckan.logic as logic
import ckan.model as model


_ = tk._
c = tk.c

log = logging.getLogger(__name__)
ckan_29_or_higher = tk.check_ckan_version(min_version="2.9.0")


def _get_flat_dict(data):
    data_dict = logic.clean_dict(
        dict_fns.unflatten(logic.tuplize_dict(logic.parse_params(data)))
    )
    return data_dict


def hero_slider_admin():
    context = {"model": model, "session": model.Session, "user": c.user or c.author}

    errors = {}
    error_summary = {}

    try:
        tk.check_access("sysadmin", context, {})
    except tk.NotAuthorized:
        tk.abort(401, _("User not authorized to view page"))

    if ckan_29_or_higher:
        form_data = _get_flat_dict(tk.request.form)
        form_data.update(_get_flat_dict(tk.request.files))
    else:
        form_data = _get_flat_dict(tk.request.POST)

    if tk.check_ckan_version(min_version="2.9.0"):
        admin_route = "heroslideradmin_blueprint.hero_slider_admin"
    else:
        admin_route = "hero_slider_admin"

    if tk.request.method == "POST":
        # Upload images to filestore
        for i in range(1, 6):
            field_url = "image_url_{}".format(i)
            image_upload = "image_upload_{}".format(i)
            clear_upload = "clear_upload_{}".format(i)

            try:
                upload = uploader.get_uploader("hero", form_data.get(field_url))
            except AttributeError:
                upload = uploader.Upload("hero", form_data.get(field_url))

            upload.update_data_dict(form_data, field_url, image_upload, clear_upload)
            upload.upload(uploader.get_max_image_size())

        # Save metadata to DB
        try:
            tk.get_action("hero_slider_update")(context, form_data)
        except tk.NotAuthorized:
            tk.abort(401, _("Unauthorized to perform that action"))
        except tk.ValidationError as e:
            errors = e.error_dict
            error_summary = e.error_summary
            h.flash_notice(error_summary)
        else:
            h.flash_success(_("The hero slider has been updated."))
        return tk.redirect_to(h.url_for(admin_route))

    hero_slider_list = tk.get_action("hero_slider_list")()

    vars = {"data": hero_slider_list, "errors": errors, "error_summary": error_summary}

    return tk.render("admin/manage_hero_slider_admin.html", extra_vars=vars)
