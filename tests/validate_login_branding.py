"""Live branding validation with protected, temporary native authentication fixtures.

Credentials and reset links must stay outside Git. The test account must be removed
by the caller after testing. Bundle requests are held only in test contexts to make
the native splash observable; the application contains no artificial loading delay.
"""

import argparse
import hashlib
import json
import re
from pathlib import Path
from time import monotonic
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright

from reybill_core import __version__
from reybill_core.branding import FAVICON, LOGIN_TITLE, LOGOS, SPLASH_ANIMATION


def validate(args):
	output = Path(args.output)
	output.mkdir(parents=True, exist_ok=True)
	results = {"version": __version__, "complete": False}
	if args.resume_presentation:
		results = json.loads((output / "browser-results.json").read_text())
		assert results["version"] == __version__
		results["complete"] = False
	errors = []
	credentials = {} if args.resume_presentation else json.loads(Path(args.credentials_file).read_text())
	with sync_playwright() as playwright:
		browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])

		def new_context(**options):
			context = browser.new_context(viewport={"width": 1440, "height": 1000}, **options)
			context.on("page", lambda page: page.on("pageerror", lambda error: errors.append(str(error))))
			return context

		def administrator(context):
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

		def favicon(page):
			paths = page.locator('link[rel*="icon"]').evaluate_all(
				"links => links.map(link => { const u = new URL(link.href); return u.pathname + u.search; })"
			)
			assert paths and set(paths) == {FAVICON}, paths
			response = page.request.get(args.url + FAVICON)
			assert response.status == 200
			assert response.headers["content-type"].startswith("image/png")
			assert response.body().startswith(b"\x89PNG\r\n\x1a\n")
			return paths

		def auth_branding(page):
			logo = page.locator("img.app-logo:visible")
			assert logo.count() == 1
			assert logo.get_attribute("src") == LOGOS["light"]
			assert logo.evaluate("image => image.complete && image.naturalWidth === 1024")
			assert logo.evaluate("image => getComputedStyle(image).filter") == "none"
			assert not re.search(r"Frappe|ERPNext", page.locator("body").inner_text())
			assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
			return {"title": page.title(), "logo": LOGOS["light"], "favicon": favicon(page)}

		def logout(page):
			page.evaluate("frappe.app.logout()")
			page.locator(".modal:visible .btn-primary").click()
			page.wait_for_url("**/login*")
			page.wait_for_load_state("networkidle")
			assert page.title() == LOGIN_TITLE
			auth_branding(page)

		if not args.resume_presentation:
			guest = new_context()
			page = guest.new_page()
			page.goto(args.url + "/login", wait_until="networkidle")
			assert page.title() == LOGIN_TITLE
			results["login"] = auth_branding(page)
			page.screenshot(path=str(output / "login-desktop.png"), full_page=True)
			page.locator(".form-login .btn-login").first.click()
			assert page.get_by_text("Email is required.", exact=True).is_visible()
			assert page.get_by_text("Password is required.", exact=True).is_visible()
			results["native_required_fields"] = "Native email/password validation retained"

			page.get_by_text("Forgot password?", exact=True).click()
			page.locator("#forgot_email").wait_for()
			results["forgot_password"] = auth_branding(page)
			page.screenshot(path=str(output / "forgot-password.png"), full_page=True)
			if args.skip_forgot_submission:
				results["forgot_password"]["native_response"] = (
					"200 generic anti-enumeration response verified in earlier runs; "
					"submission skipped on final rerun to preserve the native rate limit"
				)
			else:
				# An unregistered address exercises the real response without sending email.
				page.locator("#forgot_email").fill("unregistered-" + credentials["email"])
				with page.expect_response(
					lambda response: (
						response.request.method == "POST"
						and "frappe.core.doctype.user.user.reset_password"
						in (response.request.post_data or "")
					)
				) as response_info:
					page.locator(".btn-forgot").click()
				assert response_info.value.status == 200
				page.get_by_text("If this email is registered with us", exact=False).wait_for()
				results["forgot_password"]["native_response"] = (
					"Generic anti-enumeration response; no email sent"
				)

			page.goto(args.url + "/login", wait_until="networkidle")
			page.evaluate("continue_otp_app(true, null)")
			assert page.locator("#login_token").is_visible()
			assert not re.search(r"Frappe|ERPNext", page.locator("body").inner_text())
			results["verification_ui"] = {
				"title": page.title(),
				"favicon": favicon(page),
				"scope": "Native OTP presentation rendered only; live 2FA remains disabled and issuer unchanged",
			}
			page.screenshot(path=str(output / "verification.png"), full_page=True)

			page.goto(args.url + "/login?redirect-to=%2Fdesk", wait_until="networkidle")
			page.locator("#login_email").fill(credentials["email"])
			page.locator("#login_password").fill(credentials["password"])
			with page.expect_response("**/api/method/login") as response_info:
				page.locator(".form-login .btn-login").first.click()
			assert response_info.value.status == 200
			# Navigation can discard the response body; prove success through native Desk instead.
			page.wait_for_url("**/desk")
			page.locator(".desktop-avatar").wait_for()
			results["native_password_login"] = "Successful native password login using temporary Desk User"
			logout(page)
			results["logout_login_cycle"] = "Native logout returned to branded Login"

			reset = urlparse(credentials["reset_url"])
			page.goto(args.url + reset.path + "?" + reset.query, wait_until="networkidle")
			results["reset_password"] = auth_branding(page)
			page.screenshot(path=str(output / "reset-password.png"), full_page=True)
			assert not page.locator("#old_password").is_visible()
			page.locator("#new_password").fill(credentials["new_password"])
			page.locator("#confirm_password").fill(credentials["new_password"])
			# Native reset enables Confirm on keyup/paste, rather than the input event alone.
			page.locator("#new_password").press("End")
			page.locator("#confirm_password").press("End")
			page.locator("#update").wait_for(state="visible")
			with page.expect_response(
				lambda response: (
					response.request.method == "POST"
					and (
						"frappe.core.doctype.user.user.update_password" in response.url
						or "frappe.core.doctype.user.user.update_password"
						in (response.request.post_data or "")
					)
				)
			) as response_info:
				page.locator("#update").click()
			assert response_info.value.status == 200
			page.get_by_text("Your new password has been set successfully.", exact=True).wait_for()
			results["reset_password"]["native_reset"] = (
				"One-time native reset succeeded for temporary account"
			)
			# The native reset page may sign this account in and redirect to Desk.
			page.wait_for_url("**/desk**")
			page.locator(".desktop-avatar").wait_for()
			logout(page)
			page.locator("#login_email").fill(credentials["email"])
			page.locator("#login_password").fill(credentials["new_password"])
			page.locator(".form-login .btn-login").first.click()
			page.wait_for_url("**/desk**")
			page.locator(".desktop-avatar").wait_for()
			results["password_after_reset"] = "Native login succeeded with the newly reset password"
			logout(page)
			guest.close()

			mobile = new_context()
			mobile_page = mobile.new_page()
			mobile_page.set_viewport_size({"width": 390, "height": 844})
			mobile_page.goto(args.url + "/login", wait_until="networkidle")
			results["mobile_login"] = auth_branding(mobile_page)
			assert mobile_page.locator("#login_email").is_visible()
			assert mobile_page.locator("#login_password").is_visible()
			mobile_page.screenshot(path=str(output / "login-mobile.png"), full_page=True)
			mobile.close()

			redirect = new_context()
			redirect_page = redirect.new_page()
			deep_link = "/desk/dashboard-view/CRM"
			redirect_page.goto(args.url + deep_link, wait_until="networkidle")
			parsed = urlparse(redirect_page.url)
			assert parsed.path == "/login"
			assert parse_qs(parsed.query)["redirect-to"] == [deep_link]
			assert redirect_page.title() == LOGIN_TITLE
			results["guest_deep_link"] = "Native redirect retained /desk/dashboard-view/CRM"
			redirect.close()

		(output / "browser-results.json").write_text(json.dumps(results, indent=2) + "\n")

		desk = new_context()
		administrator(desk)
		desk_page = desk.new_page()
		desk_page.goto(args.url + "/desk", wait_until="networkidle")
		desk_page.locator(".desktop-avatar").wait_for()
		assert desk_page.title() == "Desktop"
		results["desktop"] = {"title": desk_page.title(), "favicon": favicon(desk_page)}
		desk_page.screenshot(path=str(output / "desktop.png"), full_page=True)
		desk_page.locator('.desktop-icon[data-id="CRM"]').click()
		desk_page.wait_for_function("frappe.app.sidebar.sidebar_title === 'CRM'")
		desk_page.wait_for_load_state("networkidle")
		assert desk_page.locator(".body-sidebar:visible .header-subtitle").inner_text() == "ReyBill"
		assert desk_page.get_by_text("Switch to Frappe CRM", exact=True).count() == 0
		assert desk_page.title() == "CRM Dashboard"
		results["crm"] = {"title": desk_page.title(), "favicon": favicon(desk_page)}
		desk_page.screenshot(path=str(output / "crm.png"), full_page=True)
		desk_page.reload(wait_until="networkidle")
		desk_page.wait_for_function("frappe.app.sidebar.sidebar_title === 'CRM'")
		assert desk_page.title() == "CRM Dashboard"
		favicon(desk_page)
		results["authenticated_reload_deep_link"] = "CRM deep link reloaded successfully"
		desk_page.goto(args.url + "/desk", wait_until="networkidle")
		desk_page.locator('.desktop-icon[data-id="Accounting"]').click()
		assert desk_page.locator(".modal:visible .modal-title").inner_text() == "Accounting"
		assert desk_page.title() == "Desktop"
		results["Accounting"] = {
			"folder_title": "Accounting",
			"browser_title": desk_page.title(),
			"favicon": favicon(desk_page),
			"scope": "Native Accounting item is a folder, not a workspace route",
		}
		for route, title in (("/desk/customer", "Customer"), ("/desk/sales-invoice", "Sales Invoice")):
			desk_page.goto(args.url + route, wait_until="networkidle")
			desk_page.wait_for_function("title => document.title === title", arg=title)
			results[title] = {"title": desk_page.title(), "favicon": favicon(desk_page)}
		desk_page.goto(args.url + "/desk/home", wait_until="networkidle")
		desk_page.wait_for_function("document.title === 'Home' && Boolean(frappe.workspace)")
		results["Workspace"] = {"title": desk_page.title(), "favicon": favicon(desk_page)}
		desk_page.screenshot(path=str(output / "workspace.png"), full_page=True)
		desk_page.goto(args.url + "/desk/customer", wait_until="networkidle")
		desk_page.evaluate("frappe.new_doc('Customer')")
		desk_page.locator(".modal:visible").get_by_text("Edit Full Form", exact=True).click()
		desk_page.wait_for_function("window.cur_frm?.doctype === 'Customer' && cur_frm.doc.__islocal")
		results["Customer form"] = {
			"title": desk_page.title(),
			"favicon": favicon(desk_page),
			"unsaved": True,
		}
		assert "Customer" in desk_page.title()
		assert not re.search(r"Frappe|ERPNext", desk_page.title())
		desk_page.goto(args.url + "/desk", wait_until="networkidle")
		desk_page.locator(".desktop-avatar").click()
		desk_page.locator(".context-menu:visible").get_by_text("About ReyBill", exact=True).click()
		about = desk_page.locator(".reybill-about-dialog:visible")
		assert f"ReyBill Core {__version__}" in about.inner_text()
		assert not re.search(r"Frappe|ERPNext", about.inner_text())
		about.screenshot(path=str(output / "about-v0.0.4.png"))
		results["About"] = f"ReyBill Core {__version__}; no visible vendor branding"
		assert desk_page.evaluate("frappe.boot.versions.reybill_core") == __version__
		desk.close()

		def splash_case(
			name,
			*,
			reduced_motion="no-preference",
			fail_animation=False,
			fail_script=False,
			mobile=False,
			late_animation=False,
		):
			context = new_context(reduced_motion=reduced_motion)
			administrator(context)
			requests = []
			held = []
			pending_animation = []
			context.on("request", lambda request: requests.append(urlparse(request.url).path))
			context.route("**/assets/frappe/dist/js/desk.bundle*.js", lambda route: held.append(route))
			if fail_animation:
				context.route("**" + SPLASH_ANIMATION, lambda route: route.abort())
			if late_animation:
				context.route("**" + SPLASH_ANIMATION, lambda route: pending_animation.append(route))
			if fail_script:
				context.route("**/assets/reybill_core/js/splash.js", lambda route: route.abort())
			page = context.new_page()
			if mobile:
				page.set_viewport_size({"width": 390, "height": 844})
			page.goto(args.url + "/desk", wait_until="commit")
			image = page.locator(".splash [data-reybill-splash]")
			image.wait_for()
			fallback = image.get_attribute("data-fallback")
			assert fallback in LOGOS.values()
			if page.locator("html").get_attribute("data-theme") == "dark":
				assert fallback == LOGOS["dark"]
			expected = (
				fallback
				if reduced_motion == "reduce" or fail_animation or fail_script or late_animation
				else SPLASH_ANIMATION
			)
			page.wait_for_function(
				"source => {const image = document.querySelector('[data-reybill-splash]'); return image?.getAttribute('src') === source && image.complete && image.naturalWidth > 0}",
				arg=expected,
			)
			page.wait_for_function("document.querySelector('.splash img').getBoundingClientRect().width > 0")
			assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
			page.screenshot(path=str(output / (name + ".png")), full_page=True)
			case = {
				"source": expected,
				"initial_title": page.title(),
				"fallback": expected == fallback,
			}
			if expected == SPLASH_ANIMATION:
				first = image.screenshot()
				page.wait_for_timeout(700)  # Test-only observation of the supplied SVG gradient animation.
				second = image.screenshot()
				assert hashlib.sha256(first).digest() != hashlib.sha256(second).digest()
				case["animated_pixels_changed"] = True
			if reduced_motion == "reduce":
				assert SPLASH_ANIMATION not in requests
				case["animation_not_requested"] = True
			assert not any(
				path.startswith("/assets/reybill_core/animations/") and path.endswith(".json")
				for path in requests
			)
			case["json_not_requested"] = True
			assert held, "Test must hold native startup only to observe the splash"
			start = monotonic()
			for route in held:
				route.continue_()
			page.wait_for_function("!document.querySelector('.splash')")
			case["native_removal_after_release_ms"] = round((monotonic() - start) * 1000)
			assert case["native_removal_after_release_ms"] < 4000
			page.locator(".desktop-avatar").wait_for()
			if late_animation:
				assert pending_animation
				for route in pending_animation:
					route.continue_()
				page.wait_for_load_state("networkidle")
				assert page.locator(".splash").count() == 0
				case["late_animation_did_not_block_or_restore_splash"] = True
			case["desktop_ready"] = True
			case["network_hold_is_test_only"] = True
			context.close()
			return case

		results["splash_animation"] = splash_case("splash-animation")
		results["splash_fallback"] = splash_case("splash-fallback", fail_animation=True)
		results["splash_reduced_motion"] = splash_case("splash-reduced-motion", reduced_motion="reduce")
		results["splash_script_failure"] = splash_case("splash-script-failure", fail_script=True)
		results["splash_mobile"] = splash_case("splash-mobile", mobile=True)
		results["splash_late_animation"] = splash_case("splash-late-animation", late_animation=True)
		no_js = new_context(java_script_enabled=False)
		administrator(no_js)
		no_js_page = no_js.new_page()
		no_js_page.goto(args.url + "/desk", wait_until="load")
		assert no_js_page.locator(".splash img").get_attribute("src") in LOGOS.values()
		assert no_js_page.locator(".splash img").evaluate("image => image.complete && image.naturalWidth > 0")
		results["javascript_disabled"] = "Server-rendered official static logo; no vendor fallback"
		no_js.close()
		assert not errors, errors
		results["browser_page_errors"] = errors
		results["complete"] = True
		browser.close()
	(output / "browser-results.json").write_text(json.dumps(results, indent=2) + "\n")
	print(json.dumps(results, indent=2))


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--url", default="http://reybill.localhost:8000")
	parser.add_argument("--session-file", required=True)
	parser.add_argument("--credentials-file", required=True)
	parser.add_argument("--skip-forgot-submission", action="store_true")
	parser.add_argument("--resume-presentation", action="store_true")
	parser.add_argument("--output", default="docs/validation/login-favicon-splash")
	validate(parser.parse_args())
