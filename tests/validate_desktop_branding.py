"""Live, scoped v0.0.4 Desktop checks; session stays in a protected /tmp file."""

import json
from pathlib import Path

from playwright.sync_api import sync_playwright

from reybill_core.branding import DESKTOP_LABELS, DESKTOP_ORDER, LOGOS, REYBILL_DESKTOP_ICON

SITE = "http://reybill.localhost:8000"
OUTPUT = Path("docs/validation/login-favicon-splash")
EXPECTED = [DESKTOP_LABELS.get(name, name) for name in DESKTOP_ORDER]


def validate():
	results = {}
	errors = []
	with sync_playwright() as playwright:
		browser = playwright.chromium.launch(args=["--no-sandbox"])
		context = browser.new_context(viewport={"width": 1440, "height": 1000})
		context.add_cookies(
			[
				{
					"name": "sid",
					"value": Path("/tmp/reybill_validation/session").read_text().strip(),
					"url": SITE,
					"httpOnly": True,
				}
			]
		)
		page = context.new_page()
		page.on("pageerror", lambda error: errors.append(str(error)))

		def desktop():
			page.goto(SITE + "/desk", wait_until="networkidle")
			page.locator("#brand-logo").wait_for()

		def order():
			labels = page.locator(
				".desktop-container > .icons-container > .icons > .desktop-icon .icon-title"
			).all_text_contents()
			assert labels == EXPECTED, labels
			return labels

		def artwork():
			return page.locator(
				".desktop-container > .icons-container > .icons > .desktop-icon"
			).evaluate_all(
				"icons => Object.fromEntries(icons.map(i => [i.dataset.id, i.querySelector('.icon-container')?.innerHTML]))"
			)

		def menu():
			page.locator(".desktop-avatar").click()
			return page.locator(".context-menu:visible")

		def theme(value):
			menu().get_by_text("Toggle Theme", exact=True).click()
			dialog = page.locator(".modal:visible")
			label = "Frappe Light" if value == "light" else "Timeless Night"
			with page.expect_response(
				lambda r: "switch_theme" in r.url or "switch_theme" in (r.request.post_data or "")
			):
				dialog.get_by_text(label, exact=True).click()
			page.wait_for_function("value => document.documentElement.dataset.theme === value", arg=value)
			page.wait_for_function(
				"src => document.querySelector('#brand-logo').getAttribute('src') === src", arg=LOGOS[value]
			)
			dialog.locator(".btn-modal-close").click()
			page.locator(".modal-backdrop").wait_for(state="hidden")

		desktop()
		original_theme = page.evaluate("document.documentElement.dataset.themeMode")
		before_artwork = artwork()
		results["canonical_order"] = order()
		results["workspace"] = (
			"Native Add New Workspace action appears last in edit mode; no persistent Workspace record exists."
		)
		try:
			initial_dark = page.evaluate("document.documentElement.dataset.theme === 'dark'")
			for value in ("light", "dark") if initial_dark else ("dark", "light"):
				theme(value)
				assert artwork() == before_artwork
				logo = page.locator("#brand-logo")
				assert logo.evaluate("i => i.complete && i.naturalWidth === 1024")
				results[value] = {
					"logo": logo.get_attribute("src"),
					"bounds": logo.bounding_box(),
					"runtime_switch": True,
				}
				page.screenshot(path=str(OUTPUT / f"desktop-{value}.png"), full_page=True)
				page.reload(wait_until="networkidle")
				assert page.locator("#brand-logo").get_attribute("src") == LOGOS[value]
				assert order() == EXPECTED
				assert artwork() == before_artwork
				results[value]["reload"] = True
			page.evaluate("frappe.pages.desktop.desktop_page.start_editing_layout()")
			# Select the exact removed record and its image in the nested native pane.
			removed = page.locator('.desktop-icon[data-id="ERPNext"]:visible')
			assert removed.count() == 1
			assert removed.locator("img.app-icon").get_attribute("src") == REYBILL_DESKTOP_ICON
			assert (
				page.evaluate(
					"frappe.pages.desktop.desktop_page.hidden_icons.find(i => i.name === 'ERPNext').hidden"
				)
				== 1
			)
			assert (
				page.locator(".desktop-container .icons > .add-new-icon").inner_text().strip() == "Workspace"
			)
			results["edit_mode_order"] = [*order(), "Workspace"]
			results["removed_reybill"] = {
				"internal_name": "ERPNext",
				"hidden": 1,
				"image": REYBILL_DESKTOP_ICON,
			}
			page.screenshot(path=str(OUTPUT / "desktop-removed-icon.png"), full_page=True)
			page.locator(".edit-mode-buttons .discard").click()
			assert order() == EXPECTED
			assert artwork() == before_artwork
			results["visible_artwork_unchanged_across_theme_and_reload"] = True
			# Native data default path after Reset, without deleting the user's saved layout.
			page.evaluate("""() => {
				const desktop = frappe.pages.desktop.desktop_page;
				window.reybill_validation_saved_layout = desktop.data;
				desktop.data = {};
				desktop.make();
			}""")
			assert order() == EXPECTED
			assert (
				page.evaluate(
					"frappe.pages.desktop.desktop_page.hidden_icons.find(i => i.name === 'ERPNext').hidden"
				)
				== 1
			)
			results["reset_default_render_path"] = order()
			page.evaluate(
				"frappe.pages.desktop.desktop_page.data = window.reybill_validation_saved_layout; frappe.pages.desktop.desktop_page.make()"
			)
			assert order() == EXPECTED
		finally:
			# Restore the user's actual native theme preference, including Automatic.
			page.evaluate(
				"async theme => { await frappe.xcall('frappe.core.doctype.user.user.switch_theme', {theme: theme.charAt(0).toUpperCase() + theme.slice(1)}); document.documentElement.setAttribute('data-theme-mode', theme); }",
				original_theme,
			)
			page.wait_for_timeout(100)
		context.close()
		browser.close()
	assert not errors, errors
	results["page_errors"] = errors
	(OUTPUT / "desktop-additions-results.json").write_text(json.dumps(results, indent=2) + "\n")
	print(
		"Desktop order, light/dark switching, both reloads, removed artwork and default render path passed."
	)


if __name__ == "__main__":
	validate()
