import unittest
from copy import deepcopy
from unittest.mock import patch

from reybill_core import __version__
from reybill_core.boot import extend_bootinfo, update_desk_context
from reybill_core.branding import ABOUT_ACTION, DESKTOP_LABELS, LOGOS, MENU_LABELS, SUPPORT_URL


class BootNamingTest(unittest.TestCase):
	def setUp(self):
		self.about = {
			"product_version": "16.37.0",
			"applications": [
				{"title": "ReyBill Core", "version": __version__},
				{"title": "ReyBill Farm", "version": "0.0.3"},
			],
			"company_name": "ReyBill Technologies Ltd",
		}
		patcher = patch("reybill_core.boot.get_about_data", return_value=self.about)
		patcher.start()
		self.addCleanup(patcher.stop)

	def test_presentation_preserves_source_and_navigation(self):
		messages = {"Unrelated": "Existing translation", "Framework": "Existing framework label"}
		navbar = {
			"help_dropdown": [
				{
					"name": "about-id",
					"item_label": "About",
					"item_type": "Action",
					"action": "frappe.ui.toolbar.show_about()",
				},
				{
					"name": "support-id",
					"item_label": "Frappe Support",
					"item_type": "Route",
					"route": "https://frappe.io/support",
					"hidden": 0,
				},
				{"name": "other-id", "item_label": "System Health", "route": "/desk/system-health-report"},
			],
			"settings_dropdown": [],
		}
		icons = [{"name": "Framework", "label": "Framework", "hidden": 0, "link": "/desk/build"}]
		original = deepcopy({"messages": messages, "navbar": navbar, "icons": icons})
		versions = {"frappe": "16.36.1", "erpnext": "16.37.0", "reybill_core": __version__}
		apps = [{"app_name": "erpnext", "app_title": "ERPNext", "app_route": "/desk/crm"}]
		boot = {
			"__messages": messages,
			"navbar_settings": navbar,
			"desktop_icons": icons,
			"versions": versions,
			"app_data": apps,
		}
		extend_bootinfo(boot)

		self.assertEqual({"messages": messages, "navbar": navbar, "icons": icons}, original)
		self.assertIs(boot["desktop_icons"], icons)
		for source, display in DESKTOP_LABELS.items():
			self.assertEqual(boot["__messages"][source], display)
		self.assertEqual(boot["__messages"]["Unrelated"], "Existing translation")
		self.assertNotIn("About", boot["__messages"])
		items = boot["navbar_settings"]["help_dropdown"]
		self.assertEqual(
			items[0],
			{**navbar["help_dropdown"][0], "item_label": MENU_LABELS["About"], "action": ABOUT_ACTION},
		)
		self.assertEqual(items[1]["route"], SUPPORT_URL)
		self.assertEqual(items[1]["item_label"], MENU_LABELS["Frappe Support"])
		self.assertEqual(items[1]["name"], "support-id")
		self.assertEqual(items[2], navbar["help_dropdown"][2])
		self.assertIs(boot["versions"], versions)
		self.assertIs(boot["app_data"], apps)
		self.assertEqual(apps[0]["app_title"], "ERPNext")
		self.assertEqual(boot["reybill_branding"]["about"]["applications"], self.about["applications"])
		self.assertEqual(boot["reybill_branding"]["about"]["product_version"], "16.37.0")
		self.assertEqual(boot["reybill_branding"]["about"]["logos"], LOGOS)

		first = deepcopy(boot)
		extend_bootinfo(boot)
		self.assertEqual(boot, first)

	def test_missing_navbar_and_document_navbar(self):
		boot = {}
		extend_bootinfo(boot)
		self.assertEqual(boot["reybill_branding"]["support_url"], SUPPORT_URL)

		class NavbarDocument:
			def as_dict(self):
				return {"help_dropdown": [{"item_label": "About", "action": "native()"}]}

		boot["navbar_settings"] = NavbarDocument()
		extend_bootinfo(boot)
		self.assertEqual(boot["navbar_settings"]["help_dropdown"][0]["action"], "native()")
		self.assertEqual(boot["reybill_branding"]["about"]["applications"], self.about["applications"])

	def test_final_desk_context_after_native_navbar_refresh(self):
		original_boot = {
			"navbar_settings": {
				"help_dropdown": [{"item_label": "About", "item_type": "Action", "action": "native()"}]
			},
			"another_app": "preserved",
		}
		context = {"template": "www/desk.html", "boot": original_boot}
		before = deepcopy(original_boot)
		update_desk_context(context)
		self.assertEqual(original_boot, before)
		self.assertEqual(context["boot"]["another_app"], "preserved")
		self.assertEqual(
			context["boot"]["navbar_settings"]["help_dropdown"][0]["item_label"], "About ReyBill"
		)
		self.assertEqual(context["boot"]["navbar_settings"]["help_dropdown"][0]["action"], "native()")
		for template in ("www/login.html", "www/404.html"):
			context = {"template": template, "boot": original_boot}
			update_desk_context(context)
			self.assertIs(context["boot"], original_boot)


if __name__ == "__main__":
	unittest.main()
