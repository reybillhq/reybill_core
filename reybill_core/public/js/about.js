/* ReyBill-owned customer About; native About and diagnostic data remain intact. */
frappe.provide("reybill.about");

reybill.about.show = function () {
	const branding = frappe.boot.reybill_branding;
	const about = branding.about;
	const escape = frappe.utils.escape_html;
	if (!reybill.about.dialog) {
		const dialog = new frappe.ui.Dialog({ title: __("About ReyBill") });
		$(dialog.wrapper).addClass("about-dialog reybill-about-dialog");
		reybill.about.dialog = dialog;
	}

	const dialog = reybill.about.dialog;
	const theme = frappe.ui.get_current_theme() === "dark" ? "dark" : "light";
	$(dialog.body).html(`
		<div class="about-body">
			<div class="about-frappe-section">
				<img src="${escape(about.logos[theme])}" alt="ReyBill"
					class="img-fluid reybill-about-logo" width="240">
				<div class="about-info-title">${__("ReyBill")}</div>
				<p class="about-tagline">${__("Business management software powered by ReyBill.")}</p>
				<div class="about-social-btns">
					<a href="${escape(branding.support_url)}" target="_blank"
						rel="noopener noreferrer" class="about-icon-btn" title="${__("Website")}">
						${frappe.utils.icon("globe", "sm")}
					</a>
				</div>
			</div>
			<div class="about-info-rows">
				<div class="about-info-row">
					<div class="about-info-content">
						<div class="about-info-title">${__("Version")}</div>
						<div class="about-info-sub">ReyBill Core ${escape(about.version)}</div>
					</div>
				</div>
			</div>
			<div class="about-section-label text-2xs text-ink-gray-6 text-uppercase">
				${__("Installed Applications")}
			</div>
			<div class="about-app-list">
				${about.applications
					.map(
						(label) =>
							`<div class="about-app-row"><div class="about-app-name">${escape(
								label
							)}</div></div>`
					)
					.join("")}
			</div>
		</div>
	`);
	$(dialog.footer).removeClass("hide").html('<div class="about-footer">© ReyBill Ltd</div>');
	dialog.show();
	return false;
};
