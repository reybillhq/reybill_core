"""Live module icon checks; use protected temporary sessions, never existing-user Reset."""

import argparse
import hashlib
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

from reybill_core.branding import DESKTOP_ORDER, MODULE_ICONS, branding_asset_url


def validate(args):
	out = Path(args.output)
	out.mkdir(parents=True, exist_ok=True)
	results = {
		"responsive": {},
		"accounting": {},
		"errors": [],
		"failed_icon_requests": [],
		"console_error_count": 0,
		"blocked_existing_layout_writes": [],
	}
	fixture = json.loads(Path(args.fixture_file).read_text())
	if fixture["user"] in ("Administrator", "Guest"):
		raise ValueError("Layout-reset fixture must use a disposable account, never Administrator or Guest")
	with sync_playwright() as playwright:
		browser = playwright.chromium.launch(args=["--no-sandbox"])

		def context(sid, protect_layout=False):
			ctx = browser.new_context(viewport={"width": 1440, "height": 1000})
			ctx.add_cookies([{"name": "sid", "value": sid, "url": args.url, "httpOnly": True}])
			if protect_layout:
				# Existing-user checks must never submit a layout write, even if a
				# future native interaction unexpectedly invokes Save or Reset.
				def block_layout_write(route):
					results.setdefault("blocked_existing_layout_writes", []).append(
						route.request.url.rsplit(".", 1)[-1]
					)
					route.abort()

				for method in ("save_layout", "delete_layout"):
					ctx.route(
						"**/api/method/frappe.desk.doctype.desktop_layout.desktop_layout." + method,
						block_layout_write,
					)
			page = ctx.new_page()

			def record_console(message):
				if message.type == "error":
					results["console_error_count"] += 1

			page.on("console", record_console)
			page.on("pageerror", lambda error: results["errors"].append(str(error)))
			page.on(
				"response",
				lambda response: (
					results["failed_icon_requests"].append(response.url)
					if "/module-icons/" in response.url and response.status >= 400
					else None
				),
			)
			page.on(
				"requestfailed",
				lambda request: (
					results["failed_icon_requests"].append(request.url)
					if "/module-icons/" in request.url
					else None
				),
			)
			return ctx, page

		def desktop(page):
			page.goto(args.url + "/desk", wait_until="networkidle")
			page.locator(".desktop-container > .icons-container > .icons > .desktop-icon").first.wait_for()
			page.wait_for_function(
				"Array.from(document.querySelectorAll('img.reybill-module-image')).every(i=>i.complete&&i.naturalWidth>0)"
			)

		def order(page):
			return page.locator(
				".desktop-container > .icons-container > .icons > .desktop-icon"
			).evaluate_all("icons=>icons.map(i=>i.dataset.id)")

		def inspect(page, selector):
			states = page.locator(selector).evaluate_all("""nodes=>nodes.map(node=>{
                const image=node.querySelector(':scope > .icon-container > img.reybill-module-image');
                const container=node.querySelector(':scope > .icon-container');
                const label=node.querySelector('.icon-title');
                const rect=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom};};
                const style=image?getComputedStyle(image):null;
                return {name:node.dataset.id,source:image?.getAttribute('src'),images:container?.querySelectorAll('img').length,
                    elements:container?.childElementCount,image:image?rect(image):null,container:rect(container),label:label?rect(label):null,
                    style:image?{fit:style.objectFit,filter:style.filter,width:style.width,height:style.height}:null,
                    background:getComputedStyle(container).backgroundColor,padding:getComputedStyle(container).padding,
                    shadow:getComputedStyle(container).boxShadow,natural:image?[image.naturalWidth,image.naturalHeight]:null};
            })""")
			for state in states:
				name = state["name"]
				if name not in MODULE_ICONS:
					continue
				assert state["source"] == MODULE_ICONS[name], state
				assert state["images"] == state["elements"] == 1, state
				assert state["style"]["fit"] == "contain" and state["style"]["filter"] == "none", state
				assert state["background"] == "rgba(0, 0, 0, 0)" and state["padding"] == "0px", state
				assert state["shadow"] == "none", state
				image, container, label = (state[key] for key in ("image", "container", "label"))
				assert abs(image["width"] - image["height"]) < 0.1, state
				assert image["width"] > 0 and image["right"] <= container["right"] + 0.1, state
				assert image["bottom"] <= container["bottom"] + 0.1, state
				assert label is None or image["bottom"] <= label["y"], state
				assert state["natural"][0] == state["natural"][1] and state["natural"][0] >= 512
			return states

		admin, page = context(Path(args.session_file).read_text().strip(), protect_layout=True)
		desktop(page)
		original_order = order(page)
		results["existing_user_order"] = original_order
		results["home_image"] = page.locator(
			'.desktop-icon[data-id="Home"] > .icon-container img'
		).get_attribute("src")
		assert results["home_image"] == MODULE_ICONS["Home"]
		assert page.locator('.desktop-icon[data-id="Home"] > .icon-container svg').count() == 0
		for theme in ("light", "dark"):
			for width in (1440, 1280, 768, 430, 390):
				page.set_viewport_size({"width": width, "height": 1000})
				desktop(page)
				page.evaluate("theme=>frappe.ui.set_theme(theme)", theme)
				assert order(page) == original_order
				states = inspect(page, ".desktop-container > .icons-container > .icons > .desktop-icon")
				assert sum(state["name"] in MODULE_ICONS for state in states) == 15
				results["responsive"][f"{theme}-{width}"] = states
				page.screenshot(path=str(out / f"desktop-{theme}-{width}.png"), full_page=True)
			page.set_viewport_size({"width": 1440, "height": 1000})
			desktop(page)
			page.evaluate("theme=>frappe.ui.set_theme(theme)", theme)
			page.locator('.desktop-icon[data-id="Accounting"]').click()
			page.locator('.modal:visible .desktop-icon[data-id="Banking"]').wait_for()
			page.wait_for_function(
				"Array.from(document.querySelectorAll('.modal img.reybill-module-image')).every(i=>i.complete&&i.naturalWidth>0)"
			)
			states = inspect(page, ".modal:visible .desktop-icon")
			assert len(states) == 9 and all(state["name"] in MODULE_ICONS for state in states)
			results["accounting"][theme] = states
			page.screenshot(path=str(out / f"accounting-{theme}.png"), full_page=True)
			# Native modal navigation must still work with its original tile handler.
			page.locator('.modal:visible .desktop-icon[data-id="Invoicing"]').click()
			page.wait_for_url("**/desk/invoicing*")
			page.wait_for_load_state("networkidle")
			page.locator(".body-sidebar:visible .sidebar-header img").wait_for()
			assert (
				page.locator(".body-sidebar:visible .sidebar-header img").get_attribute("src")
				== MODULE_ICONS["Invoicing"]
			)
			results["invoicing_workspace"] = {
				"route": "/desk/invoicing",
				"native_workspace_icon_slots": page.locator(".workspace-icon").count(),
				"sidebar_image": MODULE_ICONS["Invoicing"],
			}
			assert page.locator(".links-widget-box img.reybill-module-image").count() == 0
			page.locator(".body-sidebar:visible .sidebar-header").screenshot(
				path=str(out / f"invoicing-sidebar-{theme}.png")
			)
			desktop(page)
			assert order(page) == original_order

		# Accounting text-only card groups must not receive fabricated new image slots.
		results["plain_text_cards_untouched"] = True
		page.evaluate("frappe.pages.desktop.desktop_page.start_editing_layout()")
		removed = page.locator('.desktop-icon[data-id="ERPNext"]:visible img')
		assert removed.get_attribute("src") == MODULE_ICONS["ERPNext"]
		assert page.locator(".add-new-icon img.reybill-module-image").count() == 0
		results["removed_brand_and_workspace_native"] = True
		page.locator(".edit-mode-buttons .discard").click()
		results["asset_hashes"] = {}
		for asset in sorted(Path("reybill_core/public/images/branding/module-icons").glob("*.png")):
			url = branding_asset_url("images/branding/module-icons/" + asset.name)
			response = page.request.get(args.url + url)
			assert response.status == 200
			expected = hashlib.sha256(asset.read_bytes()).hexdigest()
			assert hashlib.sha256(response.body()).hexdigest() == expected
			results["asset_hashes"][asset.name] = expected
		assert not results.get("blocked_existing_layout_writes"), results
		admin.close()

		# Genuine native Reset is permitted only for this disposable account.
		isolated, page = context(fixture["sid"])
		desktop(page)
		assert page.evaluate("frappe.session.user") == fixture["user"]
		custom_order = order(page)
		assert custom_order[0] == "Home" and custom_order != list(DESKTOP_ORDER)
		inspect(page, ".desktop-container > .icons-container > .icons > .desktop-icon")
		desktop(page)
		assert order(page) == custom_order
		page.goto(args.url + "/desk/crm", wait_until="networkidle")
		desktop(page)
		assert order(page) == custom_order
		results["custom_layout_reload_and_navigation"] = True
		page.screenshot(path=str(out / "custom-layout.png"), full_page=True)
		page.locator(".desktop-avatar").click()
		with page.expect_navigation(wait_until="networkidle"):
			page.locator(".context-menu:visible").get_by_text("Reset Desktop Layout", exact=True).click()
		desktop(page)
		assert order(page) == list(DESKTOP_ORDER), order(page)
		inspect(page, ".desktop-container > .icons-container > .icons > .desktop-icon")
		results["native_reset_fixture_only"] = {"canonical_order": order(page), "existing_user_reset": False}
		page.screenshot(path=str(out / "reset-default.png"), full_page=True)
		for theme in ("Dark", "Light"):
			page.evaluate("theme=>frappe.xcall('frappe.core.doctype.user.user.switch_theme',{theme})", theme)
			desktop(page)
			assert page.evaluate("frappe.ui.get_current_theme()") == theme.lower()
			inspect(page, ".desktop-container > .icons-container > .icons > .desktop-icon")
		results["theme_reload_fixture"] = True
		isolated.close()
		browser.close()
	assert not results["errors"] and not results["failed_icon_requests"], results
	(out / "browser-results.json").write_text(json.dumps(results, indent=2) + "\n")
	print(
		"All served PNG hashes match production assets; main/Accounting mapping, both themes, 390-1440px, existing/custom layout reload/navigation and fixture-only native reset passed; zero icon request failures/page errors."
	)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--url", default="http://reybill.localhost:8000")
	parser.add_argument("--session-file", required=True)
	parser.add_argument("--fixture-file", required=True)
	parser.add_argument("--output", default="docs/validation/module-icons")
	validate(parser.parse_args())
