"""Extend Desk presentation without modifying cached source data or database records."""

from copy import deepcopy

from reybill_core.branding import DESKTOP_LABELS, MENU_LABELS, SUPPORT_URL


def extend_bootinfo(bootinfo):
	# Frappe's captions use __(), while routing continues to use the original labels.
	# Copy the dictionary: translation data may be shared with the framework cache.
	bootinfo["__messages"] = {**bootinfo.get("__messages", {}), **DESKTOP_LABELS}
	bootinfo["reybill_branding"] = {
		"menu_labels": dict(MENU_LABELS),
		"support_url": SUPPORT_URL,
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
	bootinfo["navbar_settings"] = navbar


def update_desk_context(context):
	"""Reapply presentation after v16's final session Navbar Settings refresh."""
	if context.get("template") != "www/desk.html" or not context.get("boot"):
		return
	# Keep the original session boot object untouched, including other apps' additions.
	bootinfo = dict(context["boot"])
	extend_bootinfo(bootinfo)
	context["boot"] = bootinfo
