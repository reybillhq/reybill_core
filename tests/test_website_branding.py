import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from jinja2 import Environment
from markupsafe import escape

from reybill_core.branding import FAVICON, LOGIN_TITLE, LOGOS, SYSTEM_BRANDING, WEBSITE_BRANDING
from reybill_core.setup import apply_branding
from reybill_core.website import get_splash_config, update_website_context


class WebsiteBrandingTest(unittest.TestCase):
	def test_setup_only_changes_approved_fields_and_is_idempotent(self):
		settings = {
			"Website Settings": {
				"app_name": "Frappe",
				"disable_signup": 1,
				"home_page": "existing-home",
				"title_prefix": "",
			},
			"System Settings": {
				"app_name": "Frappe",
				"otp_issuer_name": "Frappe Framework",
				"enable_two_factor_auth": 0,
				"disable_user_pass_login": 0,
			},
		}
		before = deepcopy(settings)
		with (
			patch("reybill_core.setup.frappe") as framework,
			patch("reybill_core.setup.apply_desktop_branding"),
		):
			framework.get_doc.side_effect = lambda doctype: settings[doctype]
			write = framework.db.set_single_value
			write.side_effect = lambda doctype, values: settings[doctype].update(values)
			clear = framework.clear_cache
			apply_branding()
			self.assertEqual(settings["Website Settings"], {**before["Website Settings"], **WEBSITE_BRANDING})
			self.assertEqual(settings["System Settings"], {**before["System Settings"], **SYSTEM_BRANDING})
			self.assertEqual(write.call_count, 2)
			clear.assert_called_once()
			apply_branding()
			self.assertEqual(write.call_count, 2)
			clear.assert_called_once()

	@patch("reybill_core.website._", side_effect=lambda value: value)
	def test_context_preserves_authentication_navigation_and_document_titles(self, _translate):
		for template in ("www/login.html", "www/update-password.html", "www/complete_signup.html"):
			context = {
				"template": template,
				"title": "Existing title",
				"body_class": "existing",
				"disable_signup": 1,
				"provider_logins": [{"name": "technical-provider", "auth_url": "native-url"}],
				"redirect_to": "/desk/dashboard-view/CRM",
			}
			before = deepcopy(context)
			update_website_context(context)
			self.assertEqual(context["logo"], LOGOS["light"])
			self.assertEqual(context["favicon"], FAVICON)
			self.assertIn("ReyBill", context["footer_powered"])
			self.assertNotIn("ERPNext", context["footer_powered"])
			self.assertEqual(context["body_class"], "existing reybill-auth")
			for field in ("disable_signup", "provider_logins", "redirect_to"):
				self.assertEqual(context[field], before[field])
			self.assertEqual(
				context["title"], LOGIN_TITLE if template == "www/login.html" else before["title"]
			)
			branded = deepcopy(context)
			update_website_context(context)
			self.assertEqual(context, branded)
		for title in ("CRM", "Accounting", "Customer", "Sales Invoice"):
			context = {"template": "www/desk.html", "title": title, "boot": {"versions": {"erpnext": "16"}}}
			update_website_context(context)
			self.assertEqual(context["title"], title)
			self.assertEqual(context["boot"]["versions"], {"erpnext": "16"})
			self.assertEqual(context["reybill_splash"], get_splash_config())
		unrelated = {"template": "www/custom.html", "title": "Custom page", "logo": "custom.svg"}
		before = deepcopy(unrelated)
		update_website_context(unrelated)
		self.assertEqual(unrelated, before)
		custom_footer = {"template": "www/complete_signup.html", "footer_powered": "Custom legal footer"}
		update_website_context(custom_footer)
		self.assertEqual(custom_footer["footer_powered"], "Custom legal footer")

	def test_shared_splash_include_keeps_login_script_safe_and_has_only_owned_fallback(self):
		# Native Login embeds this include inside a JS string; nested script tags break parsing.
		environment = Environment(autoescape=True)
		environment.globals["get_splash_config"] = get_splash_config
		path = Path(__file__).resolve().parents[1] / "reybill_core/templates/includes/splash_screen.html"
		template = environment.from_string(path.read_text())
		for page in ("www/login.html", "www/desk.html"):
			html = template.render(template=page)
			self.assertIn('class="centered splash"', html)
			self.assertIn(f'src="{escape(LOGOS["light"])}"', html)
			self.assertNotIn("/assets/frappe/", html)
			self.assertNotIn("/assets/erpnext/", html)
			if page == "www/login.html":
				self.assertNotIn("<script", html)
				self.assertNotIn("</script>", html)
			else:
				self.assertIn('src="/assets/reybill_core/js/splash.js"', html)
		for theme in ("light", "dark", "automatic"):
			config = get_splash_config(theme)
			html = template.render(template="www/desk.html", reybill_splash=config)
			self.assertIn(f'src="{escape(LOGOS["dark" if theme == "dark" else "light"])}"', html)
			self.assertEqual('media="(prefers-color-scheme: dark)"' in html, theme == "automatic")


if __name__ == "__main__":
	unittest.main()
