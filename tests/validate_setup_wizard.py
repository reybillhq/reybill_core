"""Offline native progress/retry/completion fixtures, never an authenticated site test.

Needs Playwright and its browser in an external test-tools directory. Reads the
installed locked native JS/CSS, blocks every network request, and writes evidence
under --output. Does not connect to Frappe, create sessions or run setup APIs.
"""

import argparse
import csv
import gettext
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT.parents[1]
FRAPPE = ROOT.parent / "frappe"

BOOTSTRAP = """
window.frappe = {
    pages: {"setup-wizard": {}}, _messages: {},
    session: {user: "Administrator"},
    ui: {Slides: class {}, Slide: class {}},
    telemetry: {can_enable: () => false},
    provide(namespace) {
        namespace.split(".").reduce((object, key) => (object[key] ||= {}), window);
    },
    set_route(...args) { window.fixtureRoutes.push(args); }
};
window.fixtureRoutes = [];
window.cint = Number;
window.cstr = String;
"""

RENDER = """
() => {
    document.getElementById("fixture").innerHTML = '<div id="native-form">Native form placeholder</div>';
    const wizard = Object.assign(Object.create(frappe.setup.SetupWizard.prototype), {
        container: $("#native-form"), parent: $("#fixture"),
        page_name: "setup-wizard", slides: [{name: "welcome"}, {name: "organization"}]
    });
    wizard.show_working_state();
    window.fixtureWizard = wizard;
    const selectors = [".setup-in-progress", ".content", ".slide-title", ".progress", ".setup-message", ".btn-abort"];
    return Object.fromEntries(selectors.map(selector => {
        const element = document.querySelector(selector);
        const rect = element.getBoundingClientRect();
        return [selector, {x: rect.x, y: rect.y, width: rect.width, height: rect.height}];
    }));
}
"""


def main():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--output", type=Path, default=Path("/tmp/reybill-core-002-validation/browser"))
	args = parser.parse_args()
	args.output.mkdir(parents=True, exist_ok=True)
	assets = json.loads((BENCH / "sites/assets/assets.json").read_text())
	native_css = (BENCH / "sites" / assets["desk.bundle.css"].lstrip("/")).read_text()
	jquery = (FRAPPE / "node_modules/jquery/dist/jquery.js").read_text()
	native_js = (FRAPPE / "frappe/desk/page/setup_wizard/setup_wizard.js").read_text()
	translator = (FRAPPE / "frappe/public/js/frappe/translate.js").read_text()
	adapter = (ROOT / "reybill_core/public/js/setup_wizard_branding.js").read_text()
	theme = (ROOT / "reybill_core/public/css/reybill_theme.css").read_text()
	with (BENCH / "sites/assets/locale/de/LC_MESSAGES/frappe.mo").open("rb") as stream:
		german = gettext.GNUTranslations(stream)
	keys = [
		"Starting Frappe ...",
		"Setting up your system",
		"Retry",
		"Setup failed",
		"Setup Complete",
		"Refreshing...",
		"Setting up company",
		"Could not start up:",
	]
	with (ROOT / "reybill_core/translations/de.csv").open(newline="") as stream:
		owned_german = {f"{source}:{context}": target for source, target, context in csv.reader(stream)}
	results = []
	with sync_playwright() as playwright:
		browser = playwright.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
		try:
			for language in ("en", "de"):
				for width in (1440, 1280, 768, 430, 390):
					context = browser.new_context(viewport={"width": width, "height": 900}, locale=language)
					context.route("**/*", lambda route: route.abort())
					page = context.new_page()
					errors = []
					page.on("pageerror", lambda error: errors.append(str(error)))
					page.set_content(
						'<!DOCTYPE html><html data-theme="light"><head><meta charset="utf-8"></head><body><main id="fixture"></main></body></html>'
					)
					page.add_style_tag(content=native_css)
					page.add_style_tag(content=theme)
					page.add_script_tag(content=jquery)
					page.add_script_tag(content=BOOTSTRAP)
					page.add_script_tag(content=translator)
					page.add_script_tag(content=native_js)
					messages = {key: german.gettext(key) for key in keys} if language == "de" else {}
					if language == "de":
						messages.update(owned_german)
					page.evaluate("messages => { frappe._messages = messages; }", messages)
					native_geometry = page.evaluate(RENDER)
					page.add_script_tag(content=adapter)
					branded_geometry = page.evaluate(RENDER)
					assert native_geometry == branded_geometry, (
						language,
						width,
						native_geometry,
						branded_geometry,
					)
					expected = "ReyBill wird gestartet..." if language == "de" else "Starting ReyBill..."
					assert page.locator(".setup-message").inner_text() == expected
					assert not any(
						name in page.locator("#fixture").inner_text()
						for name in ("Frappe", "Frappé", "ERPNext")
					)
					assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
					page.screenshot(path=str(args.output / f"{language}-{width}-starting.png"))
					page.evaluate(
						'fixtureWizard.set_setup_load_percent(50); fixtureWizard.update_setup_message(__("Setting up company"));'
					)
					assert page.locator(".progress-bar").evaluate("element => element.style.width") == "50%"
					page.evaluate(
						'fixtureWizard.abort_setup("fixture.ValidationError: diagnostic preserved");'
					)
					assert (
						page.locator(".setup-message")
						.inner_text()
						.endswith("fixture.ValidationError: diagnostic preserved")
					)
					assert page.locator(".btn-abort").is_visible()
					page.locator(".btn-abort").click()
					assert page.locator("#native-form").is_visible()
					assert page.locator(".setup-in-progress").count() == 0
					page.evaluate(RENDER)
					page.evaluate(
						'fixtureWizard.set_setup_complete_message(__("Setup Complete"), __("Refreshing..."));'
					)
					page.screenshot(path=str(args.output / f"{language}-{width}-complete.png"))
					assert not errors, errors
					results.append(
						{
							"language": language,
							"width": width,
							"starting_text": expected,
							"native_geometry_preserved": True,
							"horizontal_overflow": False,
							"progress_and_retry": "PASS",
							"completion": "PASS",
							"javascript_errors": errors,
						}
					)
					context.close()
		finally:
			browser.close()
	(args.output / "results.json").write_text(
		json.dumps(
			{
				"evidence_type": "OFFLINE NATIVE PROGRESS/RETRY/COMPLETION FIXTURES; NOT A FRESH SITE",
				"network": "ALL REQUESTS BLOCKED",
				"results": results,
			},
			indent=2,
		)
		+ "\n"
	)
	print(f"PASS: {len(results)} offline locale/viewport fixtures; evidence: {args.output}")


if __name__ == "__main__":
	main()
