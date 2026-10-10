"""Extend Desk presentation without modifying cached source data or database records."""

from copy import deepcopy

from reybill_core.about import get_about_data
from reybill_core.branding import (
	ABOUT_ACTION,
	DESKTOP_LABELS,
	EXCLUDED_DESKTOP_LAUNCHERS,
	LOGOS,
	MENU_LABELS,
	MODULE_ICONS,
	SIDEBAR_LABELS,
	SUPPORT_URL,
)
from reybill_core.desktop import filter_desktop_launchers


def extend_bootinfo(bootinfo):
	if "desktop_icons" in bootinfo:
		bootinfo["desktop_icons"] = filter_desktop_launchers(bootinfo["desktop_icons"])
	# Frappe's captions use __(), while routing continues to use the original labels.
	# Copy the dictionary: translation data may be shared with the framework cache.
	bootinfo["__messages"] = {**bootinfo.get("__messages", {}), **DESKTOP_LABELS}
	bootinfo["reybill_branding"] = {
		"excluded_desktop_launchers": [
			{"app": app, "name": name} for app, name in EXCLUDED_DESKTOP_LAUNCHERS
		],
		"menu_labels": dict(MENU_LABELS),
		"support_url": SUPPORT_URL,
		"sidebar_labels": dict(SIDEBAR_LABELS),
		"navbar_logos": dict(LOGOS),
		"module_icons": dict(MODULE_ICONS),
		"about": {
			**get_about_data(),
			"logos": dict(LOGOS),
		},
	}

	navbar = bootinfo.get("navbar_settings")
	if navbar is None:
		return
	if hasattr(navbar, "as_dict"):
		navbar = navbar.as_dict()
	# Standard menu sync keys remain unchanged in the database across migrations.
	navbar = deepcopy(navbar)
	for table in ("help_dropdown", "settings_dropdown"):
		for item in navbar.get(table, []):
			label = item.get("item_label")
			if label not in MENU_LABELS:
				continue
			item["item_label"] = MENU_LABELS[label]
			if label == "Frappe Support" and item.get("item_type") == "Route":
				item["route"] = SUPPORT_URL
			if (
				label == "About"
				and item.get("item_type") == "Action"
				and item.get("action") == "frappe.ui.toolbar.show_about()"
			):
				item["action"] = ABOUT_ACTION
	bootinfo["navbar_settings"] = navbar


def update_desk_context(context):
	"""Reapply presentation after v16's final session Navbar Settings refresh."""
	if context.get("template") != "www/desk.html" or not context.get("boot"):
		return
	# Keep the original session boot object untouched, including other apps' additions.
	bootinfo = dict(context["boot"])
	extend_bootinfo(bootinfo)
	context["boot"] = bootinfo
