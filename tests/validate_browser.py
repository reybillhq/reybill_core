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

from reybill_core.branding import DESKTOP_LABELS, MENU_LABELS, SUPPORT_URL


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

		def desktop():
			page.goto(f"{args.url}/desk", wait_until="networkidle")
			page.locator(".desktop-avatar").wait_for()

		def open_menu():
			page.locator(".desktop-avatar").click()
			return page.locator(".context-menu:visible")

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
		page.locator(".about-dialog:visible").wait_for()
		page.wait_for_function(
			'document.querySelector("#about-framework-version").textContent.includes("16.")'
		)
		results["about_dialog"] = page.locator(".about-dialog:visible").inner_text()
		assert "Frappe Framework Version" in results["about_dialog"]
		page.screenshot(path=str(output / "about-existing.png"), full_page=True)
		page.locator(".modal:visible .btn-modal-close").click()
		page.locator(".modal:visible").wait_for(state="hidden")

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
		page.locator(".body-sidebar:visible .sidebar-header").click()
		page.locator(".context-menu:visible").get_by_text("Help", exact=True).hover()
		page.locator(".context-menu:visible").get_by_text(MENU_LABELS["About"], exact=True).wait_for()
		results["help_visible_labels"] = page.locator(
			".context-menu:visible .menu-item-title"
		).all_text_contents()
		assert MENU_LABELS["Frappe Support"] in results["help_visible_labels"]
		assert "Frappe Support" not in results["help_visible_labels"]
		page.locator(".context-menu:visible").filter(
			has=page.get_by_text(MENU_LABELS["About"], exact=True)
		).screenshot(path=str(output / "help-menu.png"))

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
		browser.close()

	(output / "browser-results.json").write_text(json.dumps(results, indent=2) + "\n")
	print(json.dumps(results, indent=2))


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--url", default="http://reybill.localhost:8000")
	parser.add_argument("--session-file", required=True)
	parser.add_argument("--output", default="docs/validation")
	validate(parser.parse_args())
