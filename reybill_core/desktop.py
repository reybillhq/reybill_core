"""Canonical global Desktop defaults; user-owned layouts remain native and untouched."""

import frappe

from reybill_core.branding import DESKTOP_ORDER, EXCLUDED_DESKTOP_LAUNCHERS, REYBILL_DESKTOP_ICON


def filter_desktop_launchers(icons):
	"""Exclude only the verified redundant launcher from a presentation list."""
	filtered = [
		icon for icon in icons if (icon.get("app"), icon.get("name")) not in EXCLUDED_DESKTOP_LAUNCHERS
	]
	# Do not mutate cached rows, saved layouts or an unrelated caller's list.
	return filtered if len(filtered) != len(icons) else icons


def apply_desktop_branding():
	"""Reapply global defaults after standard import, without reading saved layouts."""
	changed = False
	for index, name in enumerate(DESKTOP_ORDER):
		if not frappe.db.exists("Desktop Icon", name):
			continue
		values = {"idx": index}
		# These are explicitly included in the approved visible canonical default.
		# Saved layouts retain their own removal states and folder relationships.
		if name in ("Home", "CRM", "Support"):
			values["hidden"] = 0
		changed |= _set_icon_fields(name, values)
	if frappe.db.exists("Desktop Icon", "ERPNext"):
		changed |= _set_icon_fields("ERPNext", {"logo_url": REYBILL_DESKTOP_ICON})
	# Native Desktop uses these defaults when no saved layout is selected.
	# DesktopPage.sync_layout() selects saved JSON otherwise, including custom idx,
	# folders and removed states. Never canonicalize or reserialize that user data.
	if changed:
		frappe.cache.delete_key("desktop_icons")
		frappe.clear_cache()


def _set_icon_fields(name, values):
	document = frappe.get_doc("Desktop Icon", name)
	changed = {field: value for field, value in values.items() if document.get(field) != value}
	if not changed:
		return False
	# Document.save() exports standard records into their owning core app in
	# developer mode. Supported db_set avoids that export and touches only fields.
	document.db_set(changed)
	return True
