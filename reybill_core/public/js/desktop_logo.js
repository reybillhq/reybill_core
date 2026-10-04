/* Only the Desktop navbar logo follows Frappe's resolved theme state. */
(() => {
	function update_logo() {
		const image = document.getElementById("brand-logo");
		const logos = frappe.boot?.reybill_branding?.navbar_logos;
		if (!image || !logos) return;
		image.setAttribute("data-reybill-logo", "");
		const theme = frappe.ui.get_current_theme() === "dark" ? "dark" : "light";
		image.setAttribute("src", logos[theme]);
	}

	// v16 routes manual and system theme changes through set_theme(), and does
	// not emit a theme event. Keep its arguments, return value and behavior intact.
	const set_theme = frappe.ui.set_theme;
	if (!set_theme.reybill_navbar_logo) {
		const set_reybill_theme = function (...args) {
			const result = set_theme.apply(this, args);
			update_logo();
			return result;
		};
		set_reybill_theme.reybill_navbar_logo = true;
		frappe.ui.set_theme = set_reybill_theme;
	}
	$(document).off("desktop_screen.reybill_logo").on("desktop_screen.reybill_logo", update_logo);
})();
