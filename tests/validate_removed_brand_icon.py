"""Read-only removed ERPNext/ReyBill artwork checks; never Save, Reset or restore."""

import argparse
import hashlib
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

from reybill_core.branding import DESKTOP_ORDER, MODULE_ICONS, REYBILL_DESKTOP_ICON

ROOT = ".desktop-container > .icons-container > .icons > .desktop-icon"


def validate(args):
	out = Path(args.output)
	out.mkdir(parents=True, exist_ok=True)
	results = {"states": {}, "blocked_layout_writes": [], "page_errors": [], "console_errors": []}
	expected = REYBILL_DESKTOP_ICON if args.baseline else MODULE_ICONS["ERPNext"]
	with sync_playwright() as playwright:
		browser = playwright.chromium.launch(args=["--no-sandbox"])
		context = browser.new_context(viewport={"width": 1440, "height": 1000})
		context.add_cookies(
			[{"name": "sid", "value": Path(args.session_file).read_text().strip(), "url": args.url}]
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
			"console",
			lambda message: (
				results["console_errors"].append({"text": message.text, "url": message.location.get("url")})
				if message.type == "error"
				else None
			),
		)

		def desktop():
			page.goto(args.url + "/desk", wait_until="networkidle")
			page.locator(ROOT).first.wait_for()

		def removed(theme, stage):
			page.evaluate("theme=>frappe.ui.set_theme(theme)", theme)
			assert page.locator(ROOT).evaluate_all("tiles=>tiles.map(t=>t.dataset.id)") == list(DESKTOP_ORDER)
			for name in ("Framework", "Home", "Accounting"):
				assert (
					page.locator(ROOT + f'[data-id="{name}"] img').get_attribute("src") == MODULE_ICONS[name]
				)
			assert page.locator(ROOT + '[data-id="ERPNext"]').count() == 0
			# The native context-menu entry is available when the floating Edit
			# button is omitted. Enter through the same native click callback.
			page.evaluate("""()=>{
                const desktop=frappe.pages.desktop.desktop_page;
                frappe.new_desktop_icons=JSON.parse(JSON.stringify(frappe.desktop_icons));
                desktop.start_editing_layout();
            }""")
			tile = page.locator('.desktop-icon[data-id="ERPNext"]:visible')
			tile.wait_for()
			page.wait_for_function("""()=>{
                const i=document.querySelector('.desktop-icon[data-id="ERPNext"] img');
                return i&&i.complete&&i.naturalWidth>0;
            }""")
			state = tile.evaluate("""tile=>{
                const box=tile.querySelector(':scope > .icon-container');
                const image=box.querySelector('img');const button=tile.querySelector('.hide-button');
                const cs=getComputedStyle(box);const callbacks=$._data(button,'events')?.click||[];
                return {id:tile.dataset.id,label:tile.querySelector('.icon-title').textContent.trim(),
                    src:image.getAttribute('src'),legacyDataLogo:tile.dataset.logo,
                    children:box.childElementCount,images:box.querySelectorAll('img').length,
                    svgs:box.querySelectorAll('svg').length,background:cs.backgroundColor,
                    shadow:cs.boxShadow,padding:cs.padding,fit:getComputedStyle(image).objectFit,
                    natural:[image.naturalWidth,image.naturalHeight],buttonMode:button.dataset.mode,
                    buttonCallbacks:callbacks.map(c=>c.handler.toString()),
                    paneOrder:frappe.pages.desktop.desktop_page.hidden_icons.map(i=>i.name),
                    hidden:frappe.desktop_icons.find(i=>i.name==='ERPNext').hidden,
                    section:tile.parentElement.parentElement.parentElement.textContent.includes('Removed Icons')};
            }""")
			assert state["id"] == "ERPNext" and state["label"] == "ReyBill"
			assert state["src"] == expected and state["section"] and state["hidden"] == 1
			assert state["buttonMode"] == "add" and state["buttonCallbacks"]
			if not args.baseline:
				assert state["children"] == state["images"] == 1 and state["svgs"] == 0
				assert state["background"] == "rgba(0, 0, 0, 0)" and state["shadow"] == "none"
				assert state["padding"] == "0px" and state["fit"] == "contain"
				assert state["natural"] == [1254, 1254]
			results["states"][f"{theme}-{stage}"] = state
			if stage == "initial":
				page.screenshot(path=str(out / f"removed-icons-{theme}.png"), full_page=True)
			# Inspect the original Add callbacks, but never click Add, Save or Reset.
			page.locator(".edit-mode-buttons .discard").click()
			assert page.locator(ROOT).evaluate_all("tiles=>tiles.map(t=>t.dataset.id)") == list(DESKTOP_ORDER)

		for theme in ("light", "dark"):
			desktop()
			removed(theme, "initial")
			page.reload(wait_until="networkidle")
			removed(theme, "reload")
			page.evaluate("frappe.set_route('/desk/invoicing')")
			page.wait_for_url("**/desk/invoicing*")
			page.evaluate("frappe.set_route('/desk')")
			page.locator(ROOT).first.wait_for()
			removed(theme, "spa-return")
		response = page.request.get(args.url + expected)
		assert response.status == 200
		asset = Path("reybill_core/public" + expected.split("?")[0].removeprefix("/assets/reybill_core"))
		assert response.body() == asset.read_bytes()
		results["served_asset"] = {
			"url": expected,
			"status": response.status,
			"sha256": hashlib.sha256(response.body()).hexdigest(),
		}
		browser.close()
	assert not results["blocked_layout_writes"] and not results["page_errors"]
	results["add_save_reset_not_invoked"] = True
	(out / "browser-results.json").write_text(json.dumps(results, indent=2) + "\n")
	print("Removed ReyBill tile passed both themes, reload and SPA return; no layout writes or resets.")


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--session-file", required=True)
	parser.add_argument("--url", default="http://reybill.localhost:8000")
	parser.add_argument("--output", default="docs/validation/removed-brand-icon")
	parser.add_argument("--baseline", action="store_true")
	validate(parser.parse_args())
