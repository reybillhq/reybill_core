"""CORE-001 presentation and native installation contracts; no live-site writes."""

import ast
import json
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import Mock, patch

from reybill_core import __version__, hooks
from reybill_core.boot import extend_bootinfo, update_desk_context
from reybill_core.branding import DESKTOP_ORDER, MODULE_ICONS
from reybill_core.desktop import filter_desktop_launchers

# Exact user-observed row on the fresh Frappe 16.36.1 site.
LAUNCHER = {
	"label": "ReyBill Core",
	"bg_color": "gray",
	"link": "/app",
	"link_type": "External",
	"app": "reybill_core",
	"icon_type": "App",
	"parent_icon": None,
	"icon": None,
	"link_to": None,
	"idx": 0,
	"standard": 0,
	"logo_url": "/assets/reybill_core/images/branding/Reybill_desk_icon.png",
	"hidden": 0,
	"name": "ReyBill Core",
	"restrict_removal": 0,
	"icon_image": None,
	"child_icons": [],
}


def canonical_icons():
	return [
		{
			"name": name,
			"label": name,
			"app": "frappe" if name == "Framework" else "erpnext",
			"idx": index,
			"hidden": 0,
			"parent_icon": None,
			"icon_type": "App" if name == "Framework" else "Link",
			"logo_url": MODULE_ICONS[name],
			"link": "/desk/original",
			"roles": ["Desk User"],
		}
		for index, name in enumerate(DESKTOP_ORDER)
	]


class DesktopLauncherTest(unittest.TestCase):
	def test_fresh_boot_removes_exact_launcher_and_preserves_registry_and_about(self):
		icons = [deepcopy(LAUNCHER), *canonical_icons()]
		before = deepcopy(icons)
		apps = [
			{"app_name": "frappe", "app_title": "Frappe Framework"},
			{"app_name": "erpnext", "app_title": "ERPNext"},
			{"app_name": "reybill_core", "app_title": "ReyBill ERP", "workspaces": []},
		]
		versions = {"frappe": "16.36.1", "erpnext": "16.37.0", "reybill_core": __version__}
		boot = {"desktop_icons": icons, "app_data": apps, "versions": versions}
		# Execute the real About helper against a mocked installed-app registry.
		with patch("reybill_core.about.frappe") as framework:
			framework.get_installed_apps.return_value = ["frappe", "erpnext", "reybill_core"]
			framework.get_hooks.return_value = ["ReyBill Core"]
			framework.get_attr.side_effect = lambda path: versions[path.removesuffix(".__version__")]
			extend_bootinfo(boot)
			self.assertEqual(framework.db.mock_calls, [])
		self.assertEqual(boot["desktop_icons"], before[1:])
		self.assertEqual([icon["name"] for icon in boot["desktop_icons"]], list(DESKTOP_ORDER))
		self.assertEqual(icons, before)
		self.assertIs(boot["app_data"], apps)
		self.assertIs(boot["versions"], versions)
		self.assertEqual(apps[2]["app_title"], "ReyBill ERP")
		self.assertEqual(
			boot["reybill_branding"]["about"]["applications"],
			[{"title": "ReyBill Core", "version": __version__}],
		)

	def test_existing_saved_layout_keeps_custom_order_fields_and_original_json(self):
		icons = canonical_icons()[::-1]
		icons.insert(4, deepcopy(LAUNCHER))
		icons.append({"name": "Personal Workspace", "app": "reybill_core", "hidden": 1, "idx": 73})
		for index, icon in enumerate(icons):
			icon.update(idx=50 + index, hidden=index % 2, parent_icon="Personal Folder")
		saved = json.dumps(icons)
		parsed = json.loads(saved)
		filtered = filter_desktop_launchers(parsed)
		self.assertEqual(filtered, [icon for icon in icons if icon["name"] != "ReyBill Core"])
		self.assertEqual(json.dumps(parsed), saved)
		self.assertEqual(parsed[4], icons[4])
		self.assertEqual(filter_desktop_launchers(filtered), filtered)

	def test_removed_icons_preserves_separate_reybill_and_other_hidden_records(self):
		removed = {**LAUNCHER, "hidden": 1}
		erpnext = {
			"name": "ERPNext",
			"app": "erpnext",
			"hidden": 1,
			"logo_url": MODULE_ICONS["ERPNext"],
			"link": "/app/home",
		}
		unrelated = {"name": "Hidden Personal Workspace", "app": "reybill_core", "hidden": 1}
		icons = [removed, erpnext, unrelated, *canonical_icons()]
		before = deepcopy(icons)
		filtered = filter_desktop_launchers(icons)
		self.assertEqual([icon for icon in filtered if icon["hidden"]], [erpnext, unrelated])
		self.assertEqual(icons, before)

	def test_identity_is_independent_of_label_grid_position_and_app_family(self):
		translated = {**LAUNCHER, "label": "Translated customer caption", "idx": 999}
		relabelled = {**LAUNCHER, "name": "Customer Shortcut"}
		other_app = {**LAUNCHER, "app": "other_app"}
		work = {**LAUNCHER, "name": "Framework", "label": "ReyBill Work"}
		missing_app = {key: value for key, value in LAUNCHER.items() if key != "app"}
		icons = [work, other_app, translated, missing_app, relabelled]
		self.assertEqual(filter_desktop_launchers(icons), [work, other_app, missing_app, relabelled])
		self.assertEqual(filter_desktop_launchers([]), [])
		self.assertIs(filter_desktop_launchers([work])[0], work)

	def test_final_desk_context_and_repeated_boot_do_not_mutate_shared_source(self):
		original = {"desktop_icons": [*canonical_icons(), deepcopy(LAUNCHER)], "other_app": "kept"}
		before = deepcopy(original)
		context = {"template": "www/desk.html", "boot": original}
		with patch("reybill_core.boot.get_about_data", return_value={}):
			update_desk_context(context)
			first = deepcopy(context["boot"])
			for _ in range(3):
				update_desk_context(context)
				self.assertEqual(context["boot"], first)
		self.assertEqual(original, before)
		self.assertEqual(context["boot"]["other_app"], "kept")
		self.assertEqual(context["boot"]["desktop_icons"], before["desktop_icons"][:-1])

	def test_native_installation_requires_registration_and_current_core_has_none(self):
		path = Path(__file__).resolve().parents[2] / "frappe/frappe/desk/doctype/desktop_icon/desktop_icon.py"
		node = next(
			node
			for node in ast.parse(path.read_text()).body
			if isinstance(node, ast.FunctionDef) and node.name == "create_desktop_icons_from_installed_apps"
		)
		module = ast.Module(body=[node], type_ignores=[])
		framework = Mock()
		framework.get_installed_apps.return_value = ["reybill_core"]
		framework.db.exists.return_value = False
		framework.get_hooks.side_effect = lambda hook, **_: (
			[hooks.app_title] if hook == "app_title" else getattr(hooks, hook, [])
		)
		namespace = {"frappe": framework, "get_app_desktop_icon": lambda _: None}
		exec(compile(module, str(path), "exec"), namespace)
		self.assertEqual(getattr(hooks, "add_to_apps_screen", []), [])
		namespace[node.name]()
		framework.new_doc.assert_not_called()

		# Verify the native registration recipe with the observed route/logo.
		# This proves the mechanism, not the record's historical provenance.
		framework.get_hooks.side_effect = lambda hook, **_: (
			[LAUNCHER["label"]]
			if hook == "app_title"
			else [{"route": LAUNCHER["link"], "logo": LAUNCHER["logo_url"]}]
		)
		document = framework.new_doc.return_value
		namespace[node.name]()
		for key in ("label", "link_type", "idx", "icon_type", "app", "link", "logo_url"):
			self.assertEqual(getattr(document, key), LAUNCHER[key])
		document.save.assert_called_once()
