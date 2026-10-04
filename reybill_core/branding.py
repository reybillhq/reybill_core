"""Customer-facing naming configuration; never use these values as identifiers."""

SUPPORT_URL = "https://reybill.com"
ABOUT_ACTION = "reybill.about.show()"

LOGOS = {
	"light": "/assets/reybill_core/images/branding/reybill-logo-black.svg",
	"dark": "/assets/reybill_core/images/branding/reybill-logo-white.svg",
}

SIDEBAR_LABELS = {
	"ERPNext": "ReyBill",
	"Frappe Framework": "ReyBill Framework",
	"Frappe": "ReyBill",
}

# Display names only; the installed app/version map remains intact.
APPLICATION_LABELS = {"erpnext": "ReyBill", "reybill_core": "ReyBill Core"}

DESKTOP_LABELS = {
	"Framework": "ReyBill Work",
	"ERPNext Settings": "ReyBill Settings",
	"ERPNext": "ReyBill",
	"Frappe Framework": "ReyBill Framework",
}

MENU_LABELS = {
	"About": "About ReyBill",
	"Frappe Support": "ReyBill Support",
}
