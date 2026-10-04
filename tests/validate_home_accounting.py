"""Read-only Home/Accounting correction validation. Blocks every layout Save/Reset."""

import argparse
import hashlib
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

from reybill_core.branding import MODULE_ICONS

ROOT_ICONS = ".desktop-container > .icons-container > .icons > .desktop-icon"


def validate(args):
	out = Path(args.output)
	out.mkdir(parents=True, exist_ok=True)
	results = {"themes": {}, "blocked_layout_writes": [], "page_errors": [], "failed_icons": []}
	with sync_playwright() as p:
		browser = p.chromium.launch(args=["--no-sandbox"])
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

		def block_write(route):
			results["blocked_layout_writes"].append(route.request.url.rsplit(".", 1)[-1])
			route.abort()

		for method in ("save_layout", "delete_layout"):
			context.route(
				"**/api/method/frappe.desk.doctype.desktop_layout.desktop_layout." + method, block_write
			)
		page = context.new_page()
		page.on("pageerror", lambda error: results["page_errors"].append(str(error)))
		page.on(
			"response",
			lambda response: (
				results["failed_icons"].append(response.url)
				if "/module-icons/" in response.url and response.status >= 400
				else None
			),
		)

		def desktop():
			page.goto(args.url + "/desk", wait_until="networkidle")
			page.locator(ROOT_ICONS).first.wait_for()
			page.wait_for_function(
				"Array.from(document.querySelectorAll('img.reybill-module-image')).every(i=>i.complete&&i.naturalWidth>0)"
			)

		def state():
			return page.locator(ROOT_ICONS).evaluate_all("""tiles=>tiles.map(tile=>{
                const box=tile.querySelector(':scope > .icon-container');
                const image=box.querySelector('img'); const cs=getComputedStyle(box);
                const style=getComputedStyle(image); const r=image.getBoundingClientRect();
                return {name:tile.dataset.id,label:tile.querySelector('.icon-title').textContent.trim(),
                    src:image.getAttribute('src'),children:box.childElementCount,images:box.querySelectorAll('img').length,
                    svgs:box.querySelectorAll('svg').length,width:r.width,height:r.height,
                    fit:style.objectFit,filter:style.filter,background:cs.backgroundColor,padding:cs.padding,
                    natural:[image.naturalWidth,image.naturalHeight]};
            })""")

		desktop()
		original_order = [tile["name"] for tile in state()]
		for theme in ("light", "dark"):
			for width in (1440, 768, 430, 390):
				page.set_viewport_size({"width": width, "height": 1000})
				desktop()  # Fresh navigation fetches the latest versioned CSS/JS/assets.
				page.evaluate("theme=>frappe.ui.set_theme(theme)", theme)
				states = state()
				assert [tile["name"] for tile in states] == original_order
				for tile in states:
					assert tile["src"] == MODULE_ICONS[tile["name"]]
					assert tile["children"] == tile["images"] == 1 and tile["svgs"] == 0
					assert tile["fit"] == "contain" and tile["filter"] == "none"
					assert tile["background"] == "rgba(0, 0, 0, 0)" and tile["padding"] == "0px"
					assert tile["width"] == tile["height"] == (50 if width < 570 else 54)
				assert {tuple(tile["natural"]) for tile in states if tile["name"] == "Accounting"} == {
					(512, 512)
				}
				results["themes"][f"{theme}-{width}"] = states
				page.screenshot(path=str(out / f"desktop-{theme}-{width}.png"), full_page=True)
			page.set_viewport_size({"width": 1440, "height": 1000})
			desktop()
			page.evaluate("theme=>frappe.ui.set_theme(theme)", theme)
			page.locator(ROOT_ICONS + '[data-id="Accounting"]').click()
			page.locator('.modal:visible .desktop-icon[data-id="Accounts Setup"]').wait_for()
			assert (
				page.locator('.modal:visible .desktop-icon[data-id="Accounts Setup"] img').get_attribute(
					"src"
				)
				== MODULE_ICONS["Accounts Setup"]
			)
			page.screenshot(path=str(out / f"accounting-folder-{theme}.png"), full_page=True)
			page.locator('.modal:visible .desktop-icon[data-id="Invoicing"]').click()
			page.wait_for_url("**/desk/invoicing*")
			desktop()
			assert [tile["name"] for tile in state()] == original_order
		results["native_folder_navigation_and_return"] = True
		# Use native translation/rendering functions, only in this browser memory.
		# No User language field or saved layout is changed.
		page.evaluate("""()=>{
            frappe._messages.Accounting='Buchhaltung';frappe._messages.Home='Start';
            const desktop=frappe.pages.desktop.desktop_page;
            desktop.make(desktop.page);desktop.setup();
        }""")
		assert page.locator(ROOT_ICONS + '[data-id="Accounting"] .icon-title').inner_text() == "Buchhaltung"
		assert page.locator(ROOT_ICONS + '[data-id="Home"] .icon-title').inner_text() == "Start"
		assert [tile["name"] for tile in state()] == original_order
		for tile in state():
			assert tile["src"] == MODULE_ICONS[tile["name"]]
		page.screenshot(path=str(out / "desktop-german-labels.png"), full_page=True)
		results["browser_only_german_labels_same_stable_mapping"] = True
		results["served_assets"] = {}
		for name in ("home", "accounting"):
			path = Path(f"reybill_core/public/images/branding/module-icons/reybill-icon-{name}.png")
			url = MODULE_ICONS["Home" if name == "home" else "Accounting"]
			response = page.request.get(args.url + url)
			assert response.status == 200 and response.body() == path.read_bytes()
			results["served_assets"][name] = {
				"url": url,
				"sha256": hashlib.sha256(response.body()).hexdigest(),
			}
		browser.close()
	assert not any(results[key] for key in ("blocked_layout_writes", "page_errors", "failed_icons")), results
	results["reset_not_invoked"] = True
	(out / "browser-results.json").write_text(json.dumps(results, indent=2) + "\n")
	print(
		"Home/Accounting corrections passed both themes, reload/rerender, four widths, German labels and native folder navigation. Zero layout writes/reset calls, icon failures or page errors."
	)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--session-file", required=True)
	parser.add_argument("--url", default="http://reybill.localhost:8000")
	parser.add_argument("--output", default="docs/validation/home-accounting")
	validate(parser.parse_args())
