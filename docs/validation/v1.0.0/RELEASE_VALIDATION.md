# ReyBill Core v1.0.0 — first major stable base release

Validated on `reybill.localhost` on 2026-10-04 with Frappe 16.36.1 and
ERPNext 16.37.0. This release promotes approved branding functionality; it does
not rename technical apps, modules, DocTypes, routes, APIs or database keys.
The historical v0.0.1–v0.0.4 tags and validation artifacts remain unchanged.

## Package and approved runtime change

`reybill_core/__init__.py` is exactly `__version__ = "1.0.0"`.
Flit's dynamic package metadata also reports 1.0.0; no second package version
declaration exists. About and owned branding URL construction derive their
version from this declaration. Historical examples and records were preserved.

The only additional UI behavior since v0.0.4 is the approved Desk logo size:

```css
.navbar-home img {
    height: 150px;
    width: auto !important;
    object-fit: contain;
}
```

The supported `app_include_css` hook includes `desk_navbar_logo.css` with the
central version/content cache key. DevTools matched rules and computed geometry
confirm 200 × 150px for the official 1024 × 768 SVG. No fixed width, stretching,
asset editing or navbar-height change is involved. Native navbar height is 52px.
The existing scoped logo adapter selects black for light and white for dark.

## Non-destructive verification

- Nine existing Python tests and five JavaScript/native-source contract tests pass.
- Ruff lint/format, ESLint, Prettier, diff whitespace and dynamic package metadata
  checks pass. Browser harnesses now use native translations; the Administrator's
  German locale was preserved rather than changed for English-only assertions.
- Login required fields, real password login, invalid password/native 401 error,
  Enter-to-submit, logout/login and login using the newly reset password pass.
  Native login scripts execute; raw JavaScript does not appear in page text.
- Forgot Password returns the native generic 200 response for a fresh unregistered
  address, without sending email. Native one-time Reset Password succeeds only for
  the temporary test account. Login/Forgot/Reset use official ReyBill branding.
- Logged-out direct CRM access retains the native redirect; login returns to the
  requested Desk route. Mobile Login remains usable at 390px.
- ReyBill favicon persists across authentication, Desktop, CRM, Workspace, list
  views, unsaved Customer form and reload. Native page titles remain intact,
  including the localized **CRM-Dashboard** title from the actual Desktop icon.
- Splash pixels animate using the supplied SVG. Animation failure, script failure,
  reduced motion and JavaScript disabled use an official static ReyBill logo.
  Reduced motion makes no animation request. A late animation cannot block or
  restore a removed splash. Native `.splash` removal completes after startup;
  network holding and animation sampling delays exist only in tests.
  No splash JSON runtime request or animation dependency is added.
- Light/dark themes, live native theme switching and reload preserve logo sources,
  150px height, original Desktop artwork and canonical order at 1440, 768, 430
  and 390px. Search opens at all four widths. Native controls remain in the viewport;
  no document-level horizontal overflow is observed.
- Desktop captions remain **ReyBill Work** and **ReyBill Settings**. Other module
  captions retain native German translations. The removed ReyBill icon stays
  removed, and the displayed response's SHA-256 equals the official PNG's hash.
- CRM sidebar remains **CRM / ReyBill**, with zero external CRM promotional banners.
  ERPNext's underlying app identity remains unchanged.
- Desktop/profile and Help **About ReyBill** open the ReyBill-owned dialog showing
  **ReyBill Core 1.0.0** and the supplied light/dark logos, without vendor branding.
  Technical framework versions and original framework About functions remain intact.
- Profile and Help **ReyBill Support** open the central `https://reybill.com`
  destination in a new tab. The external request is intercepted only by the test.
- Edit Profile, native Theme dialog, Framework navigation, ReyBill Settings,
  CRM navigation, Workspace switching to Selling, Keyboard Shortcuts, System
  Health and Logout render/operate normally. No business document is saved.
- Reset Desktop Layout is never invoked, even through an intercepted endpoint.
  Removed Icons are inspected in edit mode and discarded without saving.

## Layout, source, asset and security integrity

All six protected record-table fingerprints match before/after browser validation:
Desktop Icon, Desktop Layout, Workspace, Workspace Sidebar, Navbar Item and Has Role.
The site's existing saved Desktop layout remains byte-for-byte unchanged. No
migration or full setup runs during this release validation. Only Website Settings'
versioned branding URLs and the removed standard ReyBill icon's versioned URL are
refreshed through supported APIs; no indices, permissions, targets, artwork,
visibility states or saved layouts are changed.

The saved layout retains its prior v0.0.4 icon URL because changing it would violate
the explicit layout-preservation instruction. Its content-hash parameter and
actually served image bytes still match the current unchanged official PNG.
The canonical/default icon URL and all dynamically configured branding URLs use
v1.0.0. No global cache behavior or response headers change.

All seven official SVG/PNG/JSON asset hashes are unchanged. The six original assets
also match v0.0.3. All 3,767 tracked Frappe and 5,189 tracked ERPNext files match the
pre-milestone source baseline; neither core repository has staged changes.
ERPNext's pre-existing `banking/yarn.lock` working-tree change is unchanged and is
not part of this release. Frappe is clean.

Temporary native test User/Contact/session records and protected credential/session
files are removed. No account credentials, sessions, reset tokens, site configuration,
.env files, database dumps, node_modules, bytecode, browser profiles or temporary
logs are included. Intended validation JSON/PNG artifacts contain sanitized results
and screenshots, not browser state. The authenticator issuer remains
**Frappe Framework — NEEDS REVIEW**; it was not altered.

## Known responsive observations — preserved as approved

| Width | Observed in both themes | Decision |
| --- | --- | --- |
| 1440px / 768px | 200 × 150px image, no Search-content overflow or first-icon overlap | Preserve current behavior |
| 430px | Transparent SVG canvas overlaps the upper Framework/Home icon area | Document; no layout change |
| 390px | Search contents wrap beyond their 32px button; transparent canvas overlaps the upper Framework/Home icon area | Document; no layout change |

The wordmark remains visible and centered, but the transparent image rectangle
extends above/below the native 52px navbar. Pointer hit testing confirms that its
transparent lower area can intercept the upper part of the first two icons at
390/430px. Search still opens; there is no document-level horizontal overflow.
This is retained intentionally, not classified as resolved or silently redesigned.

## Evidence

- [Authentication, favicon, titles and splash results](authentication/browser-results.json)
- [Fresh Forgot Password, invalid password and Enter-submit results](authentication/authentication-edges.json)
- [DevTools geometry, themes, order and displayed PNG hash](navbar/branding-fixes-results.json)
- [Menus, CRM, About, support, diagnostics and navigation](menus/browser-results.json)
- [Release integrity summary and immutable asset hashes](release-integrity.json)
- [Desktop, light, 1440px](navbar/navbar-light-1440.png)
- [Desktop, dark, 1440px](navbar/navbar-dark-1440.png)
- [Known mobile behavior, 390px](navbar/navbar-light-390.png)
- [About ReyBill 1.0.0](authentication/about-v1.0.0.png)
- [CRM sidebar](menus/crm-sidebar.png)
- [Login](authentication/login-desktop.png)
- [Animated splash](authentication/splash-animation.png)

Outstanding vendor references remain classified in the
[white-label audit](../../WHITE_LABEL_AUDIT.md): native theme choices, contextual
ERPNext documentation, CRM/Support Workspace notices, external integration/help
settings, error/website surfaces outside the approved scope, email/print attribution,
and the authenticator issuer. Technical app/version identifiers remain untouched.
