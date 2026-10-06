"""Scoped website presentation without overriding authentication controllers."""

from frappe import _

from reybill_core.boot import update_desk_context
from reybill_core.branding import (
	FAVICON,
	LOGIN_TITLE,
	LOGOS,
	PRODUCT_NAME,
	SPLASH_ANIMATION,
	SPLASH_FALLBACK,
	SUPPORT_URL,
	branding_asset_url,
)


def update_website_context(context):
	# Keep the previous milestone's final Desk boot adaptation.
	update_desk_context(context)
	template = context.get("template")
	if template in ("www/login.html", "www/update-password.html", "www/complete_signup.html"):
		context["app_name"] = PRODUCT_NAME
		context["logo"] = LOGOS["light"]
		context["favicon"] = FAVICON
		# Complete Signup uses the standard website footer; an empty context falls
		# back to the ERPNext powered-by template. Preserve any explicit custom footer.
		if not context.get("footer_powered"):
			link = (
				f'<a href="{SUPPORT_URL}" target="_blank" rel="noopener noreferrer" '
				f'class="text-muted">{PRODUCT_NAME}</a>'
			)
			context["footer_powered"] = _("Powered by {0}").format(link)
		classes = (context.get("body_class") or "").split()
		if "reybill-auth" not in classes:
			classes.append("reybill-auth")
		context["body_class"] = " ".join(classes)
		if template == "www/login.html":
			context["title"] = LOGIN_TITLE
			# Use native web CSS context only here; leave public/reset routes unchanged.
			stylesheet = branding_asset_url("css/reybill_theme.css")
			includes = list(context.get("web_include_css") or [])
			if stylesheet not in includes:
				includes.append(stylesheet)
			context["web_include_css"] = includes
	if template == "www/desk.html":
		context["app_name"] = PRODUCT_NAME
		context["favicon"] = FAVICON
		context["reybill_splash"] = get_splash_config(context.get("desk_theme"))


def get_splash_config(theme=None):
	"""Also provide a static-safe default directly to the app-owned include."""
	theme = (theme or "light").lower()
	return {
		"animation": SPLASH_ANIMATION,
		"fallback": LOGOS["dark"] if theme == "dark" else SPLASH_FALLBACK,
		"dark_fallback": LOGOS["dark"],
		"automatic": theme == "automatic",
		"label": PRODUCT_NAME,
	}
