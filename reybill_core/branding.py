"""Customer-facing naming configuration; never use these values as identifiers."""

from hashlib import sha256
from pathlib import Path
from urllib.parse import urlencode

from reybill_core import __version__


def branding_asset_url(path):
	"""Stable, cacheable app-owned URL; releases and changed bytes both invalidate it."""
	asset = Path(__file__).parent / "public" / path
	parameters = {"v": __version__}
	try:
		parameters["h"] = sha256(asset.read_bytes()).hexdigest()[:12]
	except OSError:
		# An unavailable display asset must not break authentication or Desk boot.
		# Keep the owned URL and release version; never substitute vendor artwork.
		pass
	query = urlencode(parameters)
	return f"/assets/reybill_core/{path}?{query}"


SUPPORT_URL = "https://reybill.com"
ABOUT_ACTION = "reybill.about.show()"
PRODUCT_NAME = "ReyBill"
LOGIN_TITLE = "Login - ReyBill"
ABOUT_COMPANY_NAME = "ReyBill Technologies Ltd"

LOGOS = {
	"light": branding_asset_url("images/branding/reybill-logo-black.svg"),
	"dark": branding_asset_url("images/branding/reybill-logo-white.svg"),
}

FAVICON = branding_asset_url("images/branding/reybill-icon-black.png")
SPLASH_ANIMATION = branding_asset_url("animations/Splash_color_logo_gradient_loop.svg")
SPLASH_FALLBACK = LOGOS["light"]

# Only display settings: never use these values as technical app identifiers.
WEBSITE_BRANDING = {
	"app_name": PRODUCT_NAME,
	"app_logo": LOGOS["light"],
	"favicon": FAVICON,
	"splash_image": SPLASH_FALLBACK,
}
SYSTEM_BRANDING = {"app_name": PRODUCT_NAME}

# Native Desktop Icon names, never customer-facing translations or routes.
EXCLUDED_DESKTOP_LAUNCHERS = (("reybill_core", "ReyBill Core"),)

DESKTOP_ORDER = (
	"Framework",
	"Home",
	"Organization",
	"Accounting",
	"Assets",
	"Buying",
	"CRM",
	"Manufacturing",
	"Projects",
	"Quality",
	"Selling",
	"Stock",
	"Support",
	"Subcontracting",
	"ERPNext Settings",
)
REYBILL_DESKTOP_ICON = branding_asset_url("images/branding/Reybill_desk_icon.png")

# Original Desktop Icon document names; never translated labels or saved-layout data.
# Accounting stays a native Folder; its dedicated artwork preserves the composite.
MODULE_ICONS = {
	"Framework": branding_asset_url("images/branding/module-icons/reybill-icon-work.png"),
	"ERPNext": branding_asset_url("images/branding/module-icons/reybill-icon-reybill.png"),
	"Home": branding_asset_url("images/branding/module-icons/reybill-icon-home.png"),
	"Organization": branding_asset_url("images/branding/module-icons/reybill-icon-organization.png"),
	"Accounting": branding_asset_url("images/branding/module-icons/reybill-icon-accounting.png"),
	"Assets": branding_asset_url("images/branding/module-icons/reybill-icon-assets.png"),
	"Buying": branding_asset_url("images/branding/module-icons/reybill-icon-buying.png"),
	"CRM": branding_asset_url("images/branding/module-icons/reybill-icon-crm.png"),
	"Manufacturing": branding_asset_url("images/branding/module-icons/reybill-icon-manufacturing.png"),
	"Projects": branding_asset_url("images/branding/module-icons/reybill-icon-projects.png"),
	"Quality": branding_asset_url("images/branding/module-icons/reybill-icon-quality.png"),
	"Selling": branding_asset_url("images/branding/module-icons/reybill-icon-selling.png"),
	"Stock": branding_asset_url("images/branding/module-icons/reybill-icon-stock.png"),
	"Support": branding_asset_url("images/branding/module-icons/reybill-icon-support.png"),
	"Subcontracting": branding_asset_url("images/branding/module-icons/reybill-icon-subcontracting.png"),
	"ERPNext Settings": branding_asset_url("images/branding/module-icons/reybill-icon-settings.png"),
	"Accounts Setup": branding_asset_url("images/branding/module-icons/reybill-icon-accounts-setup.png"),
	"Banking": branding_asset_url("images/branding/module-icons/reybill-icon-banking.png"),
	"Budget": branding_asset_url("images/branding/module-icons/reybill-icon-budget.png"),
	"Financial Reports": branding_asset_url(
		"images/branding/module-icons/reybill-icon-financial-reports.png"
	),
	"Invoicing": branding_asset_url("images/branding/module-icons/reybill-icon-invoicing.png"),
	"Payments": branding_asset_url("images/branding/module-icons/reybill-icon-payments.png"),
	"Share Management": branding_asset_url("images/branding/module-icons/reybill-icon-share-management.png"),
	"Subscription": branding_asset_url("images/branding/module-icons/reybill-icon-subscription.png"),
	"Taxes": branding_asset_url("images/branding/module-icons/reybill-icon-taxes.png"),
}

SIDEBAR_LABELS = {
	"ERPNext": "ReyBill",
	"Frappe Framework": "ReyBill Framework",
	"Frappe": "ReyBill",
}

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
