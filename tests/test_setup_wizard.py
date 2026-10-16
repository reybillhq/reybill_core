"""Locked-v16 wizard loading and native translations; no site initialization."""

import ast
import unittest
from pathlib import Path
from unittest.mock import patch

from frappe.translate import get_translation_dict_from_file, get_translations_from_apps

from reybill_core import hooks

ROOT = Path(__file__).resolve().parents[1]
FRAPPE = ROOT.parent / "frappe" / "frappe"


class SetupWizardBrandingTest(unittest.TestCase):
	def test_native_translation_reader_loads_only_the_owned_context(self):
		path = ROOT / "reybill_core/translations/de.csv"
		self.assertEqual(
			get_translation_dict_from_file(str(path), "de", "reybill_core"),
			{"Starting ReyBill...:ReyBill Setup Wizard": "ReyBill wird gestartet..."},
		)
		# Exercise Frappe's normal app dictionary merge, without cache or DB access.
		with patch("frappe.get_app_path", side_effect=lambda app, *parts: str(ROOT / app / Path(*parts))):
			messages = get_translations_from_apps("de", apps=["reybill_core"])
		self.assertEqual(messages["Starting ReyBill...:ReyBill Setup Wizard"], "ReyBill wird gestartet...")
		self.assertNotIn("Starting Frappe ...", messages)
		self.assertNotIn("Frappe", messages)

	def test_wizard_only_asset_is_resolvable_and_keeps_desk_registration(self):
		self.assertEqual(hooks.setup_wizard_requires, "/assets/reybill_core/js/setup_wizard_branding.js")
		asset = ROOT / "reybill_core/public/js/setup_wizard_branding.js"
		self.assertTrue(asset.is_file())
		self.assertNotIn(hooks.setup_wizard_requires, hooks.app_include_js)
		self.assertEqual(hooks.page_js, {"desktop": "public/js/desktop_naming.js"})
		self.assertNotIn("setup_wizard_stages", vars(hooks))
		self.assertNotIn("setup_wizard_complete", vars(hooks))

	def test_locked_native_loading_contract_and_translation_refresh(self):
		source = (FRAPPE / "desk/page/setup_wizard/setup_wizard.js").read_text()
		self.assertLess(source.index("frappe.require(requires"), source.index('run_event("before_load")'))
		self.assertLess(
			source.index('run_event("before_load")'), source.index("new frappe.setup.SetupWizard")
		)
		self.assertIn('__("Starting Frappe ...")', source)
		boot = (FRAPPE / "boot.py").read_text()
		self.assertIn('bootinfo.setup_wizard_requires = frappe.get_hooks("setup_wizard_requires")', boot)
		tree = ast.parse((FRAPPE / "desk/page/setup_wizard/setup_wizard.py").read_text())
		loader = next(
			node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "load_messages"
		)
		self.assertIn("send_translations(get_messages_for_boot())", ast.unparse(loader))
		# Do not call load_messages: native language switching writes site preferences.
