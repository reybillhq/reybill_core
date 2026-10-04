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
