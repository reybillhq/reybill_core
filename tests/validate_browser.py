"""Optional live browser validation using an explicitly approved temporary session.

Requires Playwright and Chromium. Pass a protected session file with --session-file.
The session credential is never included in screenshots or validation output.
Reset's destructive endpoint is intercepted so existing saved layouts are preserved.
"""

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

from reybill_core import __version__
from reybill_core.branding import DESKTOP_LABELS, LOGOS, MENU_LABELS, SUPPORT_URL


def validate(args):
	results = {}
	output = Path(args.output)
	output.mkdir(parents=True, exist_ok=True)
	with sync_playwright() as playwright:
		browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
		context = browser.new_context(viewport={"width": 1440, "height": 1000})
		context.add_cookies(
			[
				{
					"name": "sid",
					"value": Path(args.session_file).read_text().strip(),
					"url": args.url,
					"httpOnly": True,
				}
			]
		)
		page = context.new_page()
		page_errors = []
		page.on("pageerror", lambda error: page_errors.append(str(error)))

		def desktop():
			page.goto(f"{args.url}/desk", wait_until="networkidle")
			page.locator(".desktop-avatar").wait_for()

		def open_menu():
			page.locator(".desktop-avatar").click()
			return page.locator(".context-menu:visible")

		def close_dialog():
			page.locator(".modal:visible .btn-modal-close").click()
			page.locator(".modal:visible").wait_for(state="hidden")

		def check_about(screenshot):
			dialog = page.locator(".reybill-about-dialog:visible")
			dialog.wait_for()
			text = dialog.inner_text()
			assert not re.search(r"Frappe|ERPNext|frappe:|erpnext:", text), text
			for phrase in (
				"About ReyBill",
				"Business management software powered by ReyBill.",
				f"ReyBill Core {__version__}",
				"INSTALLED APPLICATIONS",
				"© ReyBill Ltd",
			):
				assert phrase in text, text
			assert dialog.locator(".about-app-name").all_text_contents() == ["ReyBill", "ReyBill Core"]
			logo = dialog.locator(".reybill-about-logo")
			assert logo.get_attribute("src") == LOGOS["light"]
			assert logo.get_attribute("alt") == "ReyBill"
			assert logo.evaluate("image => image.complete && image.naturalWidth === 1024")
			assert logo.evaluate("image => getComputedStyle(image).filter") == "none"
			links = dialog.locator("a").evaluate_all(
				"links => links.map(link => ({url: link.href, target: link.target}))"
			)
			assert links == [{"url": SUPPORT_URL + "/", "target": "_blank"}], links
			dialog.screenshot(path=str(output / screenshot))
			return {"text": text, "logo": logo.get_attribute("src"), "links": links}

		def open_help():
			page.locator(".body-sidebar:visible .sidebar-header").click()
			page.locator(".context-menu:visible").get_by_text("Help", exact=True).hover()
			menu = page.locator(".context-menu:visible").filter(
				has=page.get_by_text(MENU_LABELS["About"], exact=True)
			)
			menu.get_by_text(MENU_LABELS["About"], exact=True).wait_for()
			labels = menu.locator(".menu-item-title").all_text_contents()
			# Native contextual documentation links may precede the four standard items.
			assert labels[-4:] == [
				"About ReyBill",
				"Keyboard Shortcuts",
				"System Health",
				"ReyBill Support",
			], labels
			assert "About" not in labels and "Frappe Support" not in labels, labels
			return menu

		desktop()
		for internal in ("Framework", "ERPNext Settings"):
			caption = page.locator(f'.desktop-icon[data-id="{internal}"] .icon-title').inner_text()
			assert caption == DESKTOP_LABELS[internal], (internal, caption)
			results[internal] = caption
		for internal in ("ERPNext", "Frappe Framework"):
			icons = page.locator(f'.desktop-icon[data-id="{internal}"]:visible .icon-title')
			for caption in icons.all_text_contents():
				assert caption == DESKTOP_LABELS[internal]
			assert page.evaluate("source => __(source)", internal) == DESKTOP_LABELS[internal]
			results[internal] = {"visible_icons": icons.count(), "display_mapping": DESKTOP_LABELS[internal]}

		menu = open_menu()
		labels = menu.locator(".menu-item-title").all_text_contents()
		assert labels == [
			"Edit Profile",
			"Toggle Theme",
			MENU_LABELS["About"],
			MENU_LABELS["Frappe Support"],
			"Reset Desktop Layout",
			"Logout",
		], labels
		results["profile_menu"] = labels
		page.screenshot(path=str(output / "desktop-profile.png"), full_page=True)
		menu.get_by_text(MENU_LABELS["About"], exact=True).click()
		results["about_dialog"] = check_about("about-reybill.png")
		close_dialog()
		original_theme = page.evaluate("document.documentElement.getAttribute('data-theme')")
		page.evaluate("document.documentElement.setAttribute('data-theme', 'dark')")
		open_menu().get_by_text(MENU_LABELS["About"], exact=True).click()
		logo = page.locator(".reybill-about-dialog:visible .reybill-about-logo")
		assert logo.get_attribute("src") == LOGOS["dark"]
		assert logo.evaluate("image => getComputedStyle(image).filter") == "none"
		page.locator(".reybill-about-dialog:visible").screenshot(path=str(output / "about-dark.png"))
		results["dark_logo"] = {"src": logo.get_attribute("src"), "preference_saved": False}
		close_dialog()
		page.evaluate("theme => document.documentElement.setAttribute('data-theme', theme)", original_theme)
		results["diagnostic_versions"] = page.evaluate("frappe.boot.versions")
		assert "frappe" in results["diagnostic_versions"] and "erpnext" in results["diagnostic_versions"]
		assert page.evaluate("frappe.ui.toolbar.show_about.toString().includes('frappe.ui.misc.about()')")
		assert page.evaluate("frappe.ui.misc.about.toString().includes('Frappe Framework Version')")
		results["native_about_functions"] = "Original implementations intact; customer menus use ReyBill"

		# Prove a new tab receives the configured URL without contacting the external site.
		context.route(f"{SUPPORT_URL}/**", lambda route: route.fulfill(body="Support destination verified"))
		with page.expect_popup() as popup_info:
			open_menu().get_by_text(MENU_LABELS["Frappe Support"], exact=True).click()
		popup = popup_info.value
		popup.wait_for_load_state()
		assert popup.url.rstrip("/") == SUPPORT_URL
		results["support"] = {"url": popup.url, "new_tab": True, "external_request_intercepted": True}
		popup.close()

		open_menu().get_by_text("Toggle Theme", exact=True).click()
		page.locator(".modal:visible").wait_for()
		results["theme"] = page.locator(".modal:visible").inner_text()
		page.screenshot(path=str(output / "theme-existing.png"), full_page=True)
		page.locator(".modal:visible .btn-modal-close").click()
		page.locator(".modal:visible").wait_for(state="hidden")

		open_menu().get_by_text("Edit Profile", exact=True).click()
		page.wait_for_url("**/desk/user/Administrator")
		page.wait_for_load_state("networkidle")
		results["edit_profile"] = urlparse(page.url).path
		desktop()
		page.locator('.desktop-icon[data-id="Framework"]').click()
		# With children, the native App icon opens its folder rather than its fallback link.
		page.locator(".modal:visible").wait_for()
		assert page.locator(".modal:visible .modal-title").inner_text() == DESKTOP_LABELS["Framework"]
		results["framework_folder"] = page.locator(".modal:visible .modal-title").inner_text()
		page.locator('.modal:visible .desktop-icon[data-id="Build"]').click()
		page.wait_for_url("**/desk/doctype*")
		page.wait_for_load_state("networkidle")
		page.locator(".body-sidebar:visible .sidebar-header").wait_for()
		results["framework_navigation"] = urlparse(page.url).path
		open_help().get_by_text("About ReyBill", exact=True).click()
		check_about("about-framework-help.png")
		close_dialog()
		desktop()
		page.locator('.desktop-icon[data-id="ERPNext Settings"]').click()
		page.wait_for_url("**/desk/global-defaults/Global%20Defaults*")
		page.wait_for_load_state("networkidle")
		page.wait_for_function('frappe.app.sidebar.sidebar_title === "ERPNext Settings"')
		page.locator(".body-sidebar:visible .sidebar-header").wait_for()
		assert (
			page.locator(".body-sidebar:visible .header-title").inner_text()
			== DESKTOP_LABELS["ERPNext Settings"]
		)
		results["settings_navigation"] = urlparse(page.url).path
		results["settings_sidebar_title"] = page.locator(".body-sidebar:visible .header-title").inner_text()
		results["settings_remaining_brand_terms"] = sorted(
			set(
				re.findall(
					r"Frappe Framework|Frappe Support|Frappe|ERPNext", page.locator("body").inner_text()
				)
			)
		)
		# Capture branding controls only, avoiding company settings and account details.
		page.locator(".body-sidebar:visible .sidebar-header").screenshot(
			path=str(output / "settings-navigation.png")
		)
		results["help_boot_labels"] = page.evaluate(
			"frappe.boot.navbar_settings.help_dropdown.map(item => item.item_label)"
		)
		assert MENU_LABELS["About"] in results["help_boot_labels"]
		assert MENU_LABELS["Frappe Support"] in results["help_boot_labels"]
		menu = open_help()
		results["help_visible_labels"] = menu.locator(".menu-item-title").all_text_contents()
		menu.screenshot(path=str(output / "help-menu.png"))
		menu.get_by_text("About ReyBill", exact=True).click()
		check_about("about-settings-help.png")
		close_dialog()

		desktop()
		page.locator('.desktop-icon[data-id="CRM"]').click()
		page.wait_for_load_state("networkidle")
		page.wait_for_function("frappe.app.sidebar.sidebar_title === 'CRM'")
		sidebar = page.locator(".body-sidebar:visible")
		assert sidebar.locator(".header-title").inner_text() == "CRM"
		assert sidebar.locator(".header-subtitle").inner_text() == "ReyBill"
		assert page.get_by_text("Switch to Frappe CRM", exact=True).count() == 0
		assert sidebar.locator('.promotional-banner[href*="frappe.io/crm"]').count() == 0
		assert page.evaluate("frappe.current_app.app_name") == "erpnext"
		assert page.evaluate("frappe.current_app.app_title") == "ERPNext"
		results["crm"] = {
			"title": "CRM",
			"subtitle": "ReyBill",
			"route": urlparse(page.url).path,
			"external_promotion_count": 0,
			"app_id_preserved": True,
		}
		# Capture the full branding/navigation/promotion area above the account footer.
		box = sidebar.bounding_box()
		account = sidebar.locator(".sidebar-user-button").bounding_box()
		page.screenshot(
			path=str(output / "crm-sidebar.png"),
			clip={**box, "height": account["y"] - box["y"]},
		)
		menu = open_help()
		menu.screenshot(path=str(output / "crm-help.png"))
		menu.get_by_text("About ReyBill", exact=True).click()
		check_about("about-crm-help.png")
		close_dialog()
		with page.expect_popup() as popup_info:
			open_help().get_by_text("ReyBill Support", exact=True).click()
		popup = popup_info.value
		popup.wait_for_load_state()
		assert popup.url.rstrip("/") == SUPPORT_URL
		results["help_support"] = {"url": popup.url, "new_tab": True}
		popup.close()
		open_help().get_by_text("Keyboard Shortcuts", exact=True).click()
		page.locator(".modal:visible").wait_for()
		assert page.locator(".modal:visible .modal-title").inner_text() == "Keyboard Shortcuts"
		page.locator(".modal:visible").screenshot(path=str(output / "keyboard-shortcuts.png"))
		results["keyboard_shortcuts"] = "Native dialog opened through CRM Help"
		close_dialog()
		open_help().get_by_text("System Health", exact=True).click()
		page.wait_for_url("**/desk/system-health-report*")
		page.wait_for_function("window.cur_frm?.doctype === 'System Health Report'")
		page.wait_for_load_state("networkidle")
		results["system_health"] = "Native System Health Report rendered; save remains disabled"
		assert page.evaluate("cur_frm.save_disabled")
		page.locator(".page-head:visible .title-area").screenshot(
			path=str(output / "system-health-title.png")
		)

		desktop()
		page.locator('.desktop-icon[data-id="CRM"]').click()
		page.wait_for_load_state("networkidle")
		page.locator(".body-sidebar:visible .sidebar-header").click()
		page.locator(".context-menu:visible").get_by_text("Workspaces", exact=True).hover()
		page.locator(".context-menu:visible").get_by_text("Selling", exact=True).click()
		page.wait_for_function("frappe.app.sidebar.sidebar_title === 'Selling'")
		page.wait_for_load_state("networkidle")
		results["workspace_switching"] = "Native CRM Workspaces menu switched to Selling"
		page.locator(".body-sidebar:visible .sidebar-header").screenshot(
			path=str(output / "selling-navigation.png")
		)

		desktop()
		reset_requests = []

		def intercept_reset(route):
			reset_requests.append(True)
			route.fulfill(content_type="application/json", body='{"message": null}')

		page.route(
			"**/api/method/frappe.desk.doctype.desktop_layout.desktop_layout.delete_layout", intercept_reset
		)
		page.evaluate("window.__reybill_before_reset = true")
		open_menu().get_by_text("Reset Desktop Layout", exact=True).click(no_wait_after=True)
		# Native reset and clear-cache may both reload; wait for the resulting document.
		page.wait_for_function(
			"!window.__reybill_before_reset && Boolean(window.frappe?.pages?.desktop?.desktop_page)"
		)
		page.wait_for_load_state("networkidle")
		page.locator(".desktop-avatar").wait_for()
		assert reset_requests, "Native reset action must dispatch its original method"
		results["reset"] = (
			"Native action dispatched and page reloaded; deletion endpoint intercepted to preserve layout"
		)
		assert MENU_LABELS["Frappe Support"] in open_menu().locator(".menu-item-title").all_text_contents()
		page.keyboard.press("Escape")
		open_menu().get_by_text("Logout", exact=True).click()
		page.locator(".modal:visible .btn-primary").click()
		page.wait_for_url("**/login*")
		results["logout"] = urlparse(page.url).path

		guest = browser.new_context(viewport={"width": 1440, "height": 1000})
		guest_page = guest.new_page()
		guest_page.goto(f"{args.url}/login", wait_until="networkidle")
		results["login_title"] = guest_page.title()
		results["login_text"] = guest_page.locator("body").inner_text()[:1000]
		results["login_images"] = guest_page.locator("img").evaluate_all(
			"images => images.map(image => ({src: new URL(image.src).pathname, alt: image.alt}))"
		)
		results["login_favicons"] = guest_page.locator('link[rel*="icon"]').evaluate_all(
			"links => links.map(link => new URL(link.href).pathname)"
		)
		guest_page.screenshot(path=str(output / "login-unchanged.png"), full_page=True)
		guest_page.goto(f"{args.url}/reybill-audit-page-not-found", wait_until="networkidle")
		results["error_page"] = guest_page.locator("body").inner_text()[:1000]
		assert not page_errors, page_errors
		results["browser_page_errors"] = page_errors
		browser.close()

	(output / "browser-results.json").write_text(json.dumps(results, indent=2) + "\n")
	print(json.dumps(results, indent=2))


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--url", default="http://reybill.localhost:8000")
	parser.add_argument("--session-file", required=True)
	parser.add_argument("--output", default="docs/validation/crm-help-about")
	validate(parser.parse_args())
