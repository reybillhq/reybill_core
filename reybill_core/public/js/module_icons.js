/* Approved module artwork only; native records, folders and layouts stay intact. */
(() => {
	function icon_url(name) {
		const icons = frappe.boot?.reybill_branding?.module_icons;
		return icons && Object.hasOwn(icons, name) ? icons[name] : null;
	}

	function apply_desktop_icon(icon) {
		const url = icon_url(icon.icon_data?.name);
		const container = icon.icon?.children(".icon-container").get(0);
		if (!url || !container) return;
		container.classList.add("reybill-module-icon");
		const current = container.firstElementChild;
		if (
			container.childElementCount === 1 &&
			current?.classList.contains("reybill-module-image") &&
			current.getAttribute("src") === url
		)
			return;
		const image = document.createElement("img");
		image.className = "app-icon reybill-module-image";
		image.setAttribute("src", url);
		image.setAttribute("alt", "");
		image.setAttribute("aria-hidden", "true");
		container.replaceChildren(image);
	}

	// The native utility serves only Desktop/module imagery, including sidebar
	// headers and the native Workspaces menu. Unmapped identities remain native.
	const get_desktop_icon = frappe.utils.get_desktop_icon;
	if (!get_desktop_icon.reybill_module_icons) {
		const get_reybill_desktop_icon = function (label, ...args) {
			const record = frappe.utils.get_desktop_icon_by_label(label);
			return icon_url(record?.name) || get_desktop_icon.call(this, label, ...args);
		};
		get_reybill_desktop_icon.reybill_module_icons = true;
		frappe.utils.get_desktop_icon = get_reybill_desktop_icon;
	}

	// Native Folder construction clears its thumbnail container. Adapt the
	// existing rendering method after it finishes, without changing folder data,
	// clicks, routes or grid methods. The same class builds modal/new/edit tiles.
	$(document)
		.off("desktop_screen.reybill_module_icons")
		.on("desktop_screen.reybill_module_icons", (_event, { desktop }) => {
			const icons = desktop.icon_grid?.icons || [];
			for (const icon of icons) {
				const prototype = Object.getPrototypeOf(icon);
				const render = prototype.render_folder_thumbnail;
				if (render && !render.reybill_module_icons) {
					const render_reybill_thumbnail = function (...args) {
						const result = render.apply(this, args);
						apply_desktop_icon(this);
						return result;
					};
					render_reybill_thumbnail.reybill_module_icons = true;
					prototype.render_folder_thumbnail = render_reybill_thumbnail;
				}
				apply_desktop_icon(icon);
			}
		});

	// Native Workspace pages have a separate icon slot. Change it only when it
	// exists and the actual Workspace name has a confident map entry. Plain-text
	// link cards, DocType shortcuts and form/toolbar icons are never touched.
	const workspace = frappe.views.Workspace?.prototype;
	if (workspace?.show_page && !workspace.show_page.reybill_module_icons) {
		const show_page = workspace.show_page;
		const show_reybill_workspace = async function (...args) {
			const result = await show_page.apply(this, args);
			const url = icon_url(this._page?.name);
			const slot = this.wrapper.find(".workspace-icon").get(0);
			if (url && slot) {
				const image = document.createElement("img");
				image.className = "reybill-workspace-module-image";
				image.setAttribute("src", url);
				image.setAttribute("alt", "");
				slot.replaceChildren(image);
			}
			return result;
		};
		show_reybill_workspace.reybill_module_icons = true;
		workspace.show_page = show_reybill_workspace;
	}
})();
