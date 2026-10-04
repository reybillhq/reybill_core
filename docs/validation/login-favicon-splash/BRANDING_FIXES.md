# v0.0.4 asset caching and native navbar sizing

The final release retains ReyBill-owned asset cache invalidation and restores
Frappe v16 navbar sizing. All earlier custom sizing rules, including the
320 × 150 experiment and its mobile override, are excluded from the release.

## Final implementation

- `branding.py` constructs stable owned asset URLs from the package version and
  a content fingerprint. Logo, favicon, splash and removed Desktop artwork use it.
- `desktop_branding.css` and its `app_include_css` hook were removed. No ReyBill
  navbar width, height, maximum-size, object-fit or container sizing rule remains.
- `desktop_logo.js` retains the same narrowly scoped native-theme source switching.
- Website display settings and the removed ERPNext/ReyBill artwork use the
  central URLs through the existing idempotent setup. Other icons are unchanged.
- No frontend build, global cache-policy change or animation dependency is added.

## Live validation on reybill.localhost

- DevTools matched rules are native `.navbar-home img` (width/height 32px) and
  native Desktop `#brand-logo` (width auto). Actual stylesheet origins are recorded
  in [native-navbar-css.json](native-navbar-css.json). No ReyBill Desktop CSS loads.
- The official 1024 × 768 SVG computes to about 42.65625 × 32 pixels. Navbar
  height remains 52 pixels; the complete supplied canvas and aspect ratio remain.
- Both themes, native live Toggle Theme and reload select black/light and white/dark.
- Widths 1440, 1024, 768, 430, 390 and 320 pixels pass: no overlap with Search or
  navigation, no horizontal overflow, full logo visibility and unchanged icons.
- Canonical order and the hidden/removed ReyBill state are retained. The native
  Removed Icons pane is opened and discarded, with no Save or Reset action.
- Actual displayed PNG response SHA-256:
  `c2b0e400d772a7c00450580b3a2595aff9d8d62f08f9794fbc8a2ca51857860e`.
  It matches `reybill_core/public/images/branding/Reybill_desk_icon.png` exactly,
  served with `v=0.0.4` and `h=c2b0e400d772`. Exact filename capitalization is retained.
- Native Login JavaScript executes; password fields render without raw script text.
  Logo/favicon URLs retain their owned version/content query parameters.
- Nine Python tests, five JavaScript tests, Ruff, ESLint, Prettier and whitespace
  checks pass. Core/official-asset bytes and saved-record fingerprints are verified
  separately in the final release report.

[Full browser results](branding-fixes-results.json)

Screenshots of the final native-sized logo:

- [Light desktop](navbar-light-1440.png)
- [Dark desktop](navbar-dark-1440.png)
- [Light 390px](navbar-light-390.png)
- [Dark 390px](navbar-dark-390.png)
- [Light 320px](navbar-light-320.png)
- [Dark 320px](navbar-dark-320.png)
- [Current removed Desktop icon](navbar-current-removed-icon.png)

Validation precedes the approved commit/tag. No push was performed.
