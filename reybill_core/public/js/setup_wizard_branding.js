/* Loaded only by the native Setup Wizard, before its first render. */
(() => {
	const wizard = frappe.setup?.SetupWizard?.prototype;
	if (!wizard?.get_message || wizard.get_message.reybill_setup_branding) return;

	const get_message = wizard.get_message;
	function get_reybill_setup_message(title, message, ...args) {
		// Adapt the exact native display argument before any HTML is constructed.
		// Never change the shared translator, progress events or technical errors.
		if (message === __("Starting Frappe ...")) {
			message = __("Starting ReyBill...", null, "ReyBill Setup Wizard");
		}
		return get_message.call(this, title, message, ...args);
	}
	get_reybill_setup_message.reybill_setup_branding = true;
	wizard.get_message = get_reybill_setup_message;
})();
