# ReyBill Core v0.0.4 final release verification

Verified on `reybill.localhost`, 2026-10-04, with Frappe 16.36.1 and ERPNext
16.37.0. Package version is exactly `__version__ = "0.0.4"`.

## Final navbar decision

All ReyBill navbar sizing CSS and its stylesheet hook are removed. The existing
source adapter still selects the official black SVG in light and white SVG in
dark, after native theme switching and on Desktop rendering.

Chrome DevTools attributes height to Frappe's `desk.bundle.6ZEECN56.css`
(`.navbar-home img`, 32px), and automatic width to the native Desktop page
(`#brand-logo`). The original SVG computes to about 42.65625 × 32px. No ReyBill
stylesheet controls these dimensions. [Exact origins](native-navbar-css.json).

Both themes, live native theme changes and reloads passed at widths 320, 390,
430, 768, 1024 and 1440px, with no horizontal overflow or navigation overlap.
Canonical labels/order and all visible Desktop image/symbol sources stayed
identical. [Results](branding-fixes-results.json).

## Functional validation

- Native Login, Forgot Password and Reset Password use the official black logo,
  owned favicon and ReyBill identity. Native required-field validation and Login
  JavaScript execute; raw scripts do not appear as page text.
- A temporary Desk User completed real password login, native logout, one-time
  password reset, and login with the reset password. Guest CRM deep-link redirect
  and authenticated reload retained native routes. No real user password changed.
- Browser titles retain Desktop, CRM Dashboard, Home, Customer and Sales Invoice.
  Login is Login - ReyBill; initial Desk/splash identity is ReyBill.
- Official animated SVG plays on desktop/mobile. Failed SVG/script loading,
  reduced motion and disabled JavaScript keep static ReyBill branding. Late
  animation does not restore or delay a removed splash. Native removal measured
  749–844ms after the test-only held Desk request was released; no product delay
  or minimum duration exists. JSON is retained unchanged and not loaded at runtime.
- The removed ReyBill record uses the exact supplied `Reybill_desk_icon.png`.
  Served bytes match the source hash and version/content query URL; hidden remains 1.
- CRM renders CRM / ReyBill, with no external Switch to Frappe CRM promotion.
  Internal app ID/title and installed-app switch behavior remain intact.
- Profile and Help show About ReyBill and ReyBill Support. Both About entry paths
  open the owned dialog reporting ReyBill Core 0.0.4, with no vendor branding.
  Both support actions open the centralized https://reybill.com destination in
  a new tab; external requests are intercepted only in browser validation.
- Edit Profile, Framework/settings Desktop navigation, CRM navigation, Workspace
  switching to Selling and Home Workspace navigation pass. Native Keyboard
  Shortcuts and System Health open normally, and native Logout returns to Login.

[Authentication/splash results](browser-results.json),
[menu/navigation results](release-menus/browser-results.json).

## Integrity and test limits

Nine Python tests and five JavaScript/native-source contract tests pass. Ruff
lint/format, ESLint with the existing ReyBill namespace, Prettier and Git whitespace
checks pass. Six original official assets match their original baseline and
v0.0.3 byte-for-byte; the supplied Desktop PNG remains unchanged.

All 3,767 Frappe and 5,189 ERPNext tracked file hashes match their pre-milestone
baseline. ERPNext's pre-existing banking/yarn.lock change is unrelated and
excluded. No core files are staged. No dependency, technical identity, route,
permission, business workflow or authentication configuration is changed.

Current Desktop Icon/Layout, Workspace/Sidebar, Navbar Item and Has Role table
fingerprints are identical before and after final validation and fixture cleanup.
No Reset action, layout deletion, saved-layout save or destructive layout test ran.
The approved canonical setup remains idempotent. Native Workspace is the Add New
Workspace action appended sixteenth in edit mode; no persistent icon is invented.

Temporary users, Contacts, sessions, activity and credential/reset-token files
were removed. The Administrator theme preference was restored. No credentials
or site secrets are included in release artifacts.

Forgot Password submission was not repeated, preserving its native rate limiter;
the form/branding and earlier generic response are documented. Signup, provider
authentication and real 2FA enrollment remain disabled and were not enabled for
testing. The Frappe Framework authenticator issuer stays unchanged. Remaining
theme/onboarding/email/provider/help references are recorded in
[the white-label audit](../../WHITE_LABEL_AUDIT.md).

This verification precedes the approved release commit and annotated v0.0.4 tag.
No push was performed.
