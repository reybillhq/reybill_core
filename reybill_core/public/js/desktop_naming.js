/* Desktop page extension for the installed Frappe v16 menu implementation. */
(() => {
	const event_name = "desktop_screen.reybill_naming";

	function brand_avatar_menu() {
		const branding = frappe.boot.reybill_branding;
		if (!branding) return;

		const avatar = $(".desktop-avatar").get(0);
		if (!avatar) return;
		for (const menu of Object.values(frappe.menu_map || {})) {
			if (menu.parent?.get?.(0) !== avatar) continue;
			for (const item of menu.menu_items) {
				const label = item.label;
				if (!Object.hasOwn(branding.menu_labels, label)) continue;
				item.label = branding.menu_labels[label];
				if (label === "About") {
					item.onClick = () => reybill.about.show();
				}
				if (label === "Frappe Support") {
					item.onClick = function () {
						window.open(branding.support_url, "_blank", "noopener,noreferrer");
					};
				}
			}
		}
	}

	// This native event runs before setup_avatar() on every Desktop render.
	// Wrap only this page instance; other actions and other apps' items stay native.
	$(document)
		.off(event_name)
		.on(event_name, (_event, { desktop }) => {
			if (desktop.setup_avatar.reybill_naming) return;
			const setup_avatar = desktop.setup_avatar;
			function setup_reybill_avatar(...args) {
				const result = setup_avatar.apply(this, args);
				brand_avatar_menu();
				return result;
			}
			setup_reybill_avatar.reybill_naming = true;
			desktop.setup_avatar = setup_reybill_avatar;
		});
})();
