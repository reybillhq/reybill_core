"""Install/migration defaults must never rewrite any user's persisted layout."""

import json
import unittest
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import Mock, patch

from reybill_core import hooks
from reybill_core.boot import extend_bootinfo
from reybill_core.branding import DESKTOP_ORDER, REYBILL_DESKTOP_ICON, SYSTEM_BRANDING, WEBSITE_BRANDING
from reybill_core.setup import apply_branding


def layout(custom=False, removed=False):
	names = list(reversed(DESKTOP_ORDER)) if custom else list(DESKTOP_ORDER)
	icons = [
		{
			"name": name,
			"label": name,
			"idx": index + (50 if custom else 0),
			"hidden": int(removed and name in ("Home", "CRM", "Support")),
			"parent_icon": "Personal Folder" if custom and name == "Buying" else None,
			"icon_type": "Folder" if name == "Accounting" else "Link",
			"app": "frappe" if name == "Framework" else "erpnext",
			"link": "/desk/original",
			"roles": ["Desk User"],
			"custom_field": {"preserve": True},
		}
		for index, name in enumerate(names)
	]
	icons.append({"name": "ERPNext", "hidden": 1, "logo_url": "saved-artwork.png", "idx": 300})
	if custom:
		icons.extend(
			[
				{
					"name": "Personal Folder",
					"label": "Personal Folder",
					"icon_type": "Folder",
					"app": "reybill_core",
					"idx": 900,
					"hidden": 0,
					"parent_icon": None,
					"custom_field": "keep folder metadata",
				},
				{
					"name": "Personal Shortcut",
					"label": "Personal Shortcut",
					"icon_type": "Link",
					"app": "reybill_core",
					"idx": 901,
					"hidden": 0,
					"parent_icon": "Personal Folder",
					"link": "/desk/todo",
				},
			]
		)
	return json.dumps(icons, indent=2)


class Document(dict):
	def __init__(self, doctype, name, writes, values):
		super().__init__(values)
		self.doctype = doctype
		self.name = name
		self.writes = writes

	def db_set(self, field, value=None):
		values = field if isinstance(field, dict) else {field: value}
		self.writes.append((self.doctype, self.name, deepcopy(values)))
		self.update(values)


class DesktopMigrationTest(unittest.TestCase):
	def environment(self, saved):
		framework = Mock()
		writes = []
		icons = {
			name: Document(
				"Desktop Icon",
				name,
				writes,
				{
					"idx": 100 + index,
					"hidden": 1,
					"link": "/desk/original",
					"permissions": "unchanged",
				},
			)
			for index, name in enumerate((*DESKTOP_ORDER, "ERPNext", "Unrelated"))
		}
		layouts = {
			user: Document("Desktop Layout", user, writes, {"layout": value, "user": user})
			for user, value in saved.items()
		}
		settings = {"Website Settings": dict(WEBSITE_BRANDING), "System Settings": dict(SYSTEM_BRANDING)}

		def get_doc(doctype, name=None):
			if doctype == "Desktop Icon":
				return icons[name]
			if doctype == "Desktop Layout":
				return layouts[name]
			return settings[doctype]

		framework.get_doc.side_effect = get_doc
		framework.db.exists.side_effect = lambda doctype, name: doctype == "Desktop Icon" and name in icons
		framework.get_all.side_effect = (
			lambda doctype, **kwargs: [
				SimpleNamespace(name=user, layout=doc["layout"]) for user, doc in layouts.items()
			]
			if doctype == "Desktop Layout"
			else []
		)
		return framework, writes, icons, layouts

	def run_hook(self, framework):
		self.assertEqual(hooks.after_install, "reybill_core.setup.apply_branding")
		self.assertEqual(hooks.after_migrate, hooks.after_install)
		with patch("reybill_core.desktop.frappe", framework), patch("reybill_core.setup.frappe", framework):
			apply_branding()

	def assert_preserved(self, saved):
		framework, writes, icons, layouts = self.environment(saved)
		before = {user: deepcopy(dict(doc)) for user, doc in layouts.items()}
		self.run_hook(framework)
		self.assertEqual({user: dict(doc) for user, doc in layouts.items()}, before)
		self.assertFalse(any(doctype == "Desktop Layout" for doctype, *_ in writes), writes)
		framework.get_all.assert_not_called()
		return framework, writes, icons, layouts

	def test_fresh_site_without_layout_receives_canonical_global_defaults(self):
		framework, _writes, icons, _ = self.assert_preserved({})
		before = self.environment({})[2]
		for index, name in enumerate(DESKTOP_ORDER):
			expected = {**before[name], "idx": index}
			if name in ("Home", "CRM", "Support"):
				expected["hidden"] = 0
			self.assertEqual(dict(icons[name]), expected)
		self.assertEqual(dict(icons["Unrelated"]), dict(before["Unrelated"]))
		self.assertEqual(icons["ERPNext"]["logo_url"], REYBILL_DESKTOP_ICON)
		self.assertEqual(icons["ERPNext"]["hidden"], 1)
		framework.db.set_single_value.assert_not_called()

	def test_existing_canonical_layout_remains_byte_for_byte_unchanged(self):
		self.assert_preserved({"canonical-user": layout()})

	def test_custom_order_folder_relationships_and_extra_fields_are_preserved(self):
		self.assert_preserved({"custom-user": layout(custom=True)})

	def test_removed_icons_and_saved_artwork_are_preserved(self):
		self.assert_preserved({"removed-user": layout(removed=True)})

	def test_multiple_users_keep_independent_customizations(self):
		self.assert_preserved(
			{
				"canonical": layout(),
				"custom": layout(custom=True),
				"removed": layout(custom=True, removed=True),
			}
		)

	def test_empty_and_opaque_layout_values_are_never_parsed_or_rewritten(self):
		self.assert_preserved({"empty": "", "object": "{}", "null": "null", "opaque": "legacy payload"})

	def test_repeated_hook_execution_is_idempotent_and_never_writes_layouts(self):
		framework, writes, icons, layouts = self.assert_preserved(
			{"custom": layout(custom=True, removed=True)}
		)
		before_icons = deepcopy({name: dict(doc) for name, doc in icons.items()})
		before_layouts = deepcopy({name: dict(doc) for name, doc in layouts.items()})
		count = len(writes)
		for _ in range(3):
			self.run_hook(framework)
		self.assertEqual(len(writes), count)
		self.assertEqual({name: dict(doc) for name, doc in icons.items()}, before_icons)
		self.assertEqual({name: dict(doc) for name, doc in layouts.items()}, before_layouts)
		framework.clear_cache.assert_called_once()

	def test_core_001_suppression_after_hook_keeps_the_persisted_launcher(self):
		icons = json.loads(layout(custom=True, removed=True))
		icons.append({"app": "reybill_core", "name": "ReyBill Core", "hidden": 1, "idx": 199})
		saved = {"custom": json.dumps(icons, indent=2)}
		_framework, _writes, _, layouts = self.assert_preserved(saved)
		apps = [{"app_name": "reybill_core", "app_title": "ReyBill Core"}]
		boot = {"desktop_icons": json.loads(layouts["custom"]["layout"]), "app_data": apps}
		with patch("reybill_core.boot.get_about_data", return_value={"applications": apps}):
			extend_bootinfo(boot)
		self.assertFalse(
			any(
				icon.get("app") == "reybill_core" and icon["name"] == "ReyBill Core"
				for icon in boot["desktop_icons"]
			)
		)
		self.assertEqual(layouts["custom"]["layout"], saved["custom"])
		self.assertEqual(boot["desktop_icons"], icons[:-1])
		self.assertIs(boot["app_data"], apps)
