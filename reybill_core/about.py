"""Read-only customer About metadata for the current site's installed apps."""

import frappe

from reybill_core.branding import ABOUT_COMPANY_NAME


def get_about_data():
	# Native request caching follows the site's normal install/update/cache lifecycle.
	# Never enumerate bench directories: a package on disk may belong to another site.
	installed = frappe.get_installed_apps(_ensure_on_bench=True)
	applications = [
		(app, {"title": _app_title(app), "version": _app_version(app)})
		for app in installed
		if app not in ("frappe", "erpnext")
	]
	applications.sort(key=lambda item: (item[0] != "reybill_core", item[1]["title"].casefold(), item[0]))
	return {
		"product_version": _app_version("erpnext") if "erpnext" in installed else None,
		"applications": [metadata for _, metadata in applications],
		"company_name": ABOUT_COMPANY_NAME,
	}


def _app_title(app):
	try:
		titles = frappe.get_hooks("app_title", app_name=app)
	except AttributeError, ImportError:
		titles = []
	if titles and isinstance(titles[0], str) and titles[0].strip() and titles[0].strip() != app:
		return titles[0].strip()
	if app.startswith("reybill_"):
		return "ReyBill " + app.removeprefix("reybill_").replace("_", " ").title()
	return app.replace("_", " ").title()


def _app_version(app):
	# This is the version access used by Frappe's get_versions(), without its
	# unrelated Git/branch subprocesses or a fabricated fallback version.
	try:
		version = frappe.get_attr(f"{app}.__version__")
	except AttributeError, ImportError:
		return None
	if isinstance(version, str):
		return version.strip() or None
	return None
