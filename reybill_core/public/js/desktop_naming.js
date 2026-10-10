/* Desktop page extension for the installed Frappe v16 menu implementation. */
/* global reybill */
(() => {
	const event_name = "desktop_screen.reybill_naming";

	function filter_launchers(icons) {
		const exclusions = frappe.boot.reybill_branding?.excluded_desktop_launchers || [];
		if (!Array.isArray(icons) || !exclusions.length) return icons;
		const filtered = icons.filter(
			(icon) =>
				!exclusions.some((entry) => icon.app === entry.app && icon.name === entry.name)
		);
		return filtered.length === icons.length ? icons : filtered;
	}

	function install_launcher_filter(desktop) {
		if (!desktop?.prepare || desktop.prepare.reybill_launcher_filter) return;
		const prepare = desktop.prepare;
		function prepare_reybill_desktop(...args) {
			// Native sync_layout can restore the original saved array on each render.
			// Filter only runtime input; never write this.data, storage or the database.
			const key = this.edit_mode ? "new_desktop_icons" : "desktop_icons";
			frappe[key] = filter_launchers(frappe[key]);
			return prepare.apply(this, args);
		}
		prepare_reybill_desktop.reybill_launcher_filter = true;
		desktop.prepare = prepare_reybill_desktop;
	}

	// page_js runs after native page definitions and before on_page_load/show.
	// Install before the first grid/Removed Icons preparation, not after rendering.
	const page = frappe.pages?.desktop;
	const on_page_load = page?.on_page_load;
	if (on_page_load && !on_page_load.reybill_launcher_filter) {
		const load_reybill_desktop = function (...args) {
			const result = on_page_load.apply(this, args);
			install_launcher_filter(page.desktop_page);
			return result;
		};
		load_reybill_desktop.reybill_launcher_filter = true;
		page.on_page_load = load_reybill_desktop;
	}
	install_launcher_filter(page?.desktop_page);

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
