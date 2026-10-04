"""Canonical ordering through native Desktop Icon and Desktop Layout data."""

import json

import frappe

from reybill_core.branding import DESKTOP_ORDER, REYBILL_DESKTOP_ICON


def order_layout(icons):
	"""Change only approved indices and the removed ERPNext/ReyBill artwork."""
	ranks = {name: index for index, name in enumerate(DESKTOP_ORDER)}
	for icon in icons:
		name = icon.get("name")
		if name in ranks:
			icon["idx"] = ranks[name]
		if name == "ERPNext":
			icon["logo_url"] = REYBILL_DESKTOP_ICON
	return icons


def apply_desktop_branding():
	"""Idempotent settings, reapplied after native standard-record import."""
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
	for row in frappe.get_all("Desktop Layout", fields=["name", "layout"]):
		if not row.layout:
			continue
		icons = json.loads(row.layout)
		if not isinstance(icons, list):
			# Native empty/default layouts may be stored as {} rather than [].
			continue
		before = json.dumps(icons, sort_keys=True)
		order_layout(icons)
		if json.dumps(icons, sort_keys=True) != before:
			frappe.get_doc("Desktop Layout", row.name).db_set("layout", json.dumps(icons))
			changed = True
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
