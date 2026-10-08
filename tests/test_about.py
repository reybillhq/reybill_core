"""Current-site About inventory tests; no site installs, removals or DB writes."""

import unittest
from unittest.mock import patch

from reybill_core.about import get_about_data


class AboutDataTest(unittest.TestCase):
	def setUp(self):
		patcher = patch("reybill_core.about.frappe")
		self.framework = patcher.start()
		self.addCleanup(patcher.stop)
		self.installed = ["frappe", "erpnext", "reybill_farm", "reybill_core"]
		self.titles = {"reybill_core": "ReyBill Core", "reybill_farm": "ReyBill Farm"}
		self.versions = {
			"frappe": "16.36.1",
			"erpnext": "16.37.0",
			"reybill_core": "1.0.0",
			"reybill_farm": "0.0.3",
			"reybill_water": "0.1.0",
		}
		self.framework.get_installed_apps.side_effect = lambda **_: list(self.installed)
		self.framework.get_hooks.side_effect = lambda hook, app_name: (
			[self.titles[app_name]] if app_name in self.titles else []
		)
		self.framework.get_attr.side_effect = lambda path: self.versions[path.removesuffix(".__version__")]

	def test_current_site_product_components_and_minimal_payload(self):
		data = get_about_data()
		self.assertEqual(
			data,
			{
				"product_version": "16.37.0",
				"applications": [
					{"title": "ReyBill Core", "version": "1.0.0"},
					{"title": "ReyBill Farm", "version": "0.0.3"},
				],
				"company_name": "ReyBill Technologies Ltd",
			},
		)
		self.framework.get_installed_apps.assert_called_once_with(_ensure_on_bench=True)
		self.framework.get_attr.assert_any_call("erpnext.__version__")
		self.assertNotIn(
			"frappe.__version__", [call.args[0] for call in self.framework.get_attr.call_args_list]
		)

	def test_versions_are_resolved_again_after_an_app_update(self):
		before = get_about_data()
		self.versions.update(erpnext="16.40.2", reybill_farm="0.0.4")
		after = get_about_data()
		self.assertEqual(before["product_version"], "16.37.0")
		self.assertEqual(after["product_version"], "16.40.2")
		self.assertEqual(after["applications"][1]["version"], "0.0.4")
		self.assertEqual(after["applications"][0], before["applications"][0])

	def test_future_apps_metadata_fallbacks_and_stable_core_first_order(self):
		self.installed.extend(["reybill_water", "commerce", "reybill_animal_health", "other_tool"])
		self.titles.update(commerce="Acme Commerce", reybill_animal_health="ReyBill Animal Care")
		self.versions.update(commerce="2.3.4", reybill_animal_health="0.2.0", other_tool="3.0.0")
		data = get_about_data()
		self.assertEqual(
			data["applications"],
			[
				{"title": "ReyBill Core", "version": "1.0.0"},
				{"title": "Acme Commerce", "version": "2.3.4"},
				{"title": "Other Tool", "version": "3.0.0"},
				{"title": "ReyBill Animal Care", "version": "0.2.0"},
				{"title": "ReyBill Farm", "version": "0.0.3"},
				{"title": "ReyBill Water", "version": "0.1.0"},
			],
		)
		self.installed.reverse()
		self.assertEqual(get_about_data(), data)

	def test_removed_or_other_site_app_is_not_listed_or_inspected(self):
		self.assertEqual(len(get_about_data()["applications"]), 2)
		self.installed.remove("reybill_farm")
		self.framework.get_hooks.reset_mock()
		self.framework.get_attr.reset_mock()
		data = get_about_data()
		self.assertEqual(data["applications"], [{"title": "ReyBill Core", "version": "1.0.0"}])
		self.assertEqual(
			[call.kwargs["app_name"] for call in self.framework.get_hooks.call_args_list], ["reybill_core"]
		)
		self.assertNotIn(
			"reybill_farm.__version__", [call.args[0] for call in self.framework.get_attr.call_args_list]
		)
		self.assertNotIn(
			"reybill_water.__version__", [call.args[0] for call in self.framework.get_attr.call_args_list]
		)

	def test_missing_or_empty_versions_and_title_fail_gracefully(self):
		self.installed.extend(["reybill_water", "no_metadata"])
		self.titles["reybill_farm"] = "reybill_farm"
		self.versions.update(reybill_core=None, reybill_farm="", reybill_water="  ")

		def version(path):
			if path == "erpnext.__version__":
				raise AttributeError("No version attribute")
			if path == "no_metadata.__version__":
				raise ImportError("No importable version metadata")
			return self.versions[path.removesuffix(".__version__")]

		self.framework.get_attr.side_effect = version
		data = get_about_data()
		self.assertIsNone(data["product_version"])
		self.assertEqual(data["applications"][0]["title"], "ReyBill Core")
		self.assertTrue(all(app["version"] is None for app in data["applications"]))
		self.assertIn({"title": "ReyBill Farm", "version": None}, data["applications"])

	def test_empty_site_has_no_fake_product_app_or_version(self):
		self.installed = []
		self.assertEqual(
			get_about_data(),
			{"product_version": None, "applications": [], "company_name": "ReyBill Technologies Ltd"},
		)
		self.framework.get_hooks.assert_not_called()
		self.framework.get_attr.assert_not_called()
