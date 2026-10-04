"""Idempotent setup of the explicitly approved customer-facing settings."""

import frappe

from reybill_core.branding import SYSTEM_BRANDING, WEBSITE_BRANDING
from reybill_core.desktop import apply_desktop_branding


def apply_branding():
	"""Use the supported Single-setting API; preserve every unrelated setting."""
	updated = False
	for doctype, values in (
		("Website Settings", WEBSITE_BRANDING),
		("System Settings", SYSTEM_BRANDING),
	):
		document = frappe.get_doc(doctype)
		changed = {field: value for field, value in values.items() if document.get(field) != value}
		if changed:
			# Saving all System Settings can normalize authentication/password fields.
			# Write only the approved display fields through Frappe's settings API.
			frappe.db.set_single_value(doctype, changed)
			updated = True
	if updated:
		frappe.clear_cache()
	apply_desktop_branding()
