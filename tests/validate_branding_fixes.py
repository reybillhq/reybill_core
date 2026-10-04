"""Live checks for asset freshness, approved navbar sizing and theme switching."""

import hashlib
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright

from reybill_core import __version__
from reybill_core.branding import DESKTOP_ORDER, FAVICON, LOGOS, REYBILL_DESKTOP_ICON

SITE = "http://reybill.localhost:8000"
OUTPUT = Path(f"docs/validation/v{__version__}/navbar")


def validate():
	OUTPUT.mkdir(parents=True, exist_ok=True)
	results = {"version": __version__, "responsive": {}}
	errors = []
	asset = Path("reybill_core/public/images/branding/Reybill_desk_icon.png")
	expected_hash = hashlib.sha256(asset.read_bytes()).hexdigest()
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
		page.goto(SITE + "/desk", wait_until="networkidle")
		page.locator("#brand-logo").wait_for()
		original_theme = page.evaluate("document.documentElement.dataset.themeMode")

		def artwork():
			return page.locator(
				".desktop-container > .icons-container > .icons > .desktop-icon"
			).evaluate_all(
				"""icons => Object.fromEntries(icons.map(i => [i.dataset.id, {
					images: Array.from(i.querySelectorAll('.icon-container img'), n => n.getAttribute('src')),
					symbols: Array.from(i.querySelectorAll('.icon-container svg use'), n => n.getAttribute('href'))
				}]))"""
			)

		original_artwork = artwork()
		expected_order = page.evaluate("names => names.map(name => __(name))", list(DESKTOP_ORDER))
		results["desktop_labels"] = expected_order
		try:
			for theme in ("light", "dark"):
				if page.evaluate("document.documentElement.dataset.themeMode") != theme:
					page.locator(".desktop-avatar").click()
					page.locator(".context-menu:visible").get_by_text(
						page.evaluate("__('Toggle Theme')"), exact=True
					).click()
					dialog = page.locator(".modal:visible")
					with page.expect_response(
						lambda r: "switch_theme" in r.url or "switch_theme" in (r.request.post_data or "")
					):
						dialog.get_by_text(
							page.evaluate(
								"name => __(name)", "Frappe Light" if theme == "light" else "Timeless Night"
							),
							exact=True,
						).click()
					dialog.locator(".btn-modal-close").click()
					page.locator(".modal-backdrop").wait_for(state="hidden")
				page.wait_for_function(
					"src => document.querySelector('#brand-logo').getAttribute('src') === src",
					arg=LOGOS[theme],
				)
				for width in (1440, 768, 430, 390):
					page.set_viewport_size({"width": width, "height": 1000})
					if width < 768:
						# Let native Desktop initialize its mobile grid at the target width.
						page.reload(wait_until="networkidle")
					geometry = page.evaluate("""() => {
						const box = selector => { const r = document.querySelector(selector).getBoundingClientRect();
						return {x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom}; };
						return {logo:box('#brand-logo'),navbar:box('.desktop-navbar'),
							search:box('.desktop-search-wrapper'),navigation:box('.desktop-navbar > .flex'),
							overflow:document.documentElement.scrollWidth>innerWidth,
							fit:getComputedStyle(document.querySelector('#brand-logo')).objectFit};
					}""")
					logo, navbar, search, navigation = (
						geometry[key] for key in ("logo", "navbar", "search", "navigation")
					)
					assert logo["height"] == 150 and abs(logo["width"] - 150 * 1024 / 768) < 0.02
					assert navbar["height"] == 52 and not geometry["overflow"]
					assert logo["right"] <= search["x"] and search["right"] <= navigation["x"]
					assert navigation["right"] <= navbar["right"]
					assert abs((logo["y"] + logo["height"] / 2) - (navbar["y"] + navbar["height"] / 2)) <= 1
					assert (
						geometry["fit"] == "contain"
					)  # The approved logo preserves its official SVG aspect ratio.
					# Verify the cascade using Chrome DevTools' matched stylesheet rules.
					cdp = context.new_cdp_session(page)
					cdp.send("DOM.enable")
					cdp.send("CSS.enable")
					root = cdp.send("DOM.getDocument")["root"]["nodeId"]
					node = cdp.send("DOM.querySelector", {"nodeId": root, "selector": "#brand-logo"})[
						"nodeId"
					]
					matched = cdp.send("CSS.getMatchedStylesForNode", {"nodeId": node})["matchedCSSRules"]
					sizing_rules = []
					for match in matched:
						rule = match["rule"]
						selector = rule["selectorList"]["text"]
						if selector not in ("#brand-logo", ".navbar-home img"):
							continue
						properties = {p["name"]: p["value"] for p in rule["style"]["cssProperties"]}
						if selector == "#brand-logo":
							assert properties.get("width") == "auto"
						elif properties.get("height") == "150px":
							assert properties.get("width") == "auto !important"
							assert properties.get("object-fit") == "contain"
						else:
							assert properties.get("height") == "32px" and properties.get("width") == "32px"
						sizing_rules.append({"selector": selector, "properties": properties})
					assert len([r for r in sizing_rules if r["properties"].get("height") == "150px"]) == 1
					assert page.locator('link[href*="desktop_branding.css"]').count() == 0
					cdp.detach()
					geometry["matched_sizing_rules"] = sizing_rules
					assert artwork() == original_artwork
					assert (
						page.locator(
							".desktop-container > .icons-container > .icons > .desktop-icon .icon-title"
						).all_text_contents()
						== expected_order
					)
					geometry["known_responsive_observations"] = page.evaluate("""() => {
                        const search = document.querySelector('#desktop-navbar-modal-search');
                        const label = search.querySelector('span');
                        const searchBox = search.getBoundingClientRect();
                        const labelBox = label.getBoundingClientRect();
                        const icons = Array.from(document.querySelectorAll('.desktop-container > .icons-container > .icons > .desktop-icon')).slice(0,2);
                        return {search_contents_outside_button:labelBox.top<searchBox.top || labelBox.bottom>searchBox.bottom,
                            first_icons:icons.map(icon => {const r=icon.querySelector('.icon-container').getBoundingClientRect();
                                const hit=document.elementFromPoint(r.x+r.width/2,r.y+2);
                                return {name:icon.dataset.id,top_hit_brand_logo:hit?.id==='brand-logo'};})};
                    }""")
					page.locator("#desktop-navbar-modal-search").click()
					page.locator("#navbar-search:visible").wait_for()
					page.keyboard.press("Escape")
					geometry["search_opened"] = True
					results["responsive"][f"{theme}-{width}"] = geometry
					if width in (1440, 768, 430, 390):
						page.screenshot(path=str(OUTPUT / f"navbar-{theme}-{width}.png"), full_page=True)
				page.set_viewport_size({"width": 1440, "height": 1000})
				page.reload(wait_until="networkidle")
				assert page.locator("#brand-logo").get_attribute("src") == LOGOS[theme]
				assert page.locator("#brand-logo").bounding_box()["height"] == 150
				assert artwork() == original_artwork
				results[f"{theme}_switch_and_reload"] = True

			# Inspect Removed Icons, then discard; never save/reset a user's layout.
			page.evaluate("frappe.pages.desktop.desktop_page.start_editing_layout()")
			image = page.locator('.desktop-icon[data-id="ERPNext"]:visible img.app-icon')
			image.wait_for()
			displayed_url = image.get_attribute("src")
			assert urlparse(displayed_url).path == urlparse(REYBILL_DESKTOP_ICON).path
			response = page.request.get(SITE + displayed_url)
			assert response.status == 200
			served_hash = hashlib.sha256(response.body()).hexdigest()
			assert served_hash == expected_hash
			assert image.evaluate("i => i.complete && i.naturalWidth === 2133")
			assert (
				page.evaluate(
					"frappe.pages.desktop.desktop_page.hidden_icons.find(i => i.name === 'ERPNext').hidden"
				)
				== 1
			)
			query = parse_qs(urlparse(image.get_attribute("src")).query)
			assert query.get("h") == [expected_hash[:12]] and query.get("v")
			# Existing saved layouts retain their versioned URL; identical artwork remains valid.
			assert parse_qs(urlparse(REYBILL_DESKTOP_ICON).query)["v"] == [__version__]
			results["desktop_asset"] = {
				"source_file": str(asset),
				"current_default_url": REYBILL_DESKTOP_ICON,
				"saved_layout_url_preserved": True,
				"displayed_url": image.get_attribute("src"),
				"source_sha256": expected_hash,
				"displayed_response_sha256": served_hash,
				"removed": True,
			}
			page.screenshot(path=str(OUTPUT / "navbar-current-removed-icon.png"), full_page=True)
			page.locator(".edit-mode-buttons .discard").click()
			assert artwork() == original_artwork
		finally:
			page.evaluate(
				"async theme => { await frappe.xcall('frappe.core.doctype.user.user.switch_theme', {theme:theme.charAt(0).toUpperCase()+theme.slice(1)});document.documentElement.setAttribute('data-theme-mode',theme); }",
				original_theme,
			)
		context.close()
		guest = browser.new_page()
		guest.goto(SITE + "/login", wait_until="networkidle")
		assert guest.title() == "Login - ReyBill"
		assert guest.evaluate("typeof login") == "object"
		assert "login.call" not in guest.locator("body").inner_text()
		assert guest.locator("img.app-logo:visible").get_attribute("src") == LOGOS["light"]
		assert guest.locator("#login_password").is_visible()
		favicon = guest.locator('link[rel="shortcut icon"]').get_attribute("href")
		assert favicon == FAVICON
		results["native_login_smoke"] = {
			"javascript_executes": True,
			"logo": LOGOS["light"],
			"favicon": favicon,
		}
		browser.close()
	assert not errors, errors
	results["page_errors"] = errors
	(OUTPUT / "branding-fixes-results.json").write_text(json.dumps(results, indent=2) + "\n")
	print(
		"Displayed PNG bytes match source; approved 150px aspect-ratio sizing, both themes, reload, canonical order and 390-1440px widths passed; native login smoke passed."
	)


if __name__ == "__main__":
	validate()
