/* Adapt sidebar presentation before the native v16 header/banner rendering. */
(() => {
	const event_name = "sidebar_setup.reybill_branding";

	$(document)
		.off(event_name)
		.on(event_name, (_event, { sidebar }) => {
			if (!frappe.boot.reybill_branding) return;
			if (!sidebar.choose_app_name.reybill_branding) {
				const choose_app_name = sidebar.choose_app_name;
				const choose_reybill_subtitle = function (...args) {
					const result = choose_app_name.apply(this, args);
					const labels = frappe.boot.reybill_branding.sidebar_labels;
					if (Object.hasOwn(labels, this.header_subtitle)) {
						this.header_subtitle = labels[this.header_subtitle];
					}
					return result;
				};
				choose_reybill_subtitle.reybill_branding = true;
				sidebar.choose_app_name = choose_reybill_subtitle;
			}

			if (!sidebar.get_crm_banner.reybill_branding) {
				const get_crm_banner = sidebar.get_crm_banner;
				const get_reybill_crm_banner = function (module) {
					const start = this.promotional_banners.length;
					const result = get_crm_banner.call(this, module);
					if (module === "CRM") {
						// Remove only external promotions produced by this native method.
						// Keep any installed CRM app link and all unrelated banners.
						const retained = this.promotional_banners
							.slice(start)
							.filter((banner) => banner.is_internal);
						this.promotional_banners.splice(start, Infinity, ...retained);
					}
					return result;
				};
				get_reybill_crm_banner.reybill_branding = true;
				sidebar.get_crm_banner = get_reybill_crm_banner;
			}
		});
})();
