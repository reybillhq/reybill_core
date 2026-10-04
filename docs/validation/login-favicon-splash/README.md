# ReyBill Core 0.0.4 validation

Validated on `reybill.localhost` (`http://reybill.localhost:8000`) on
2026-10-04, with installed Frappe 16.36.1 / ERPNext 16.37.0. This report records
validation before the approved release commit/tag. No push was performed.
[Every changed file](CHANGED_FILES.md) is listed
separately; [browser-results.json](browser-results.json) contains observed values.

## Implementation and deployment

- Supported Website Settings fields: `app_name = ReyBill`, official black
  `app_logo`, original black PNG `favicon`, static black `splash_image` fallback.
- Supported System Settings display field: `app_name = ReyBill`.
- Idempotent setup ran directly twice; the second execution changed nothing.
  Install/migrate hooks apply the same five display fields on subsequent setup.
- Site cache was cleared. No schema migration or asset rebuild was needed for
  plain app JS/CSS and the small app-owned Jinja include.
- Late website context retains prior Desk boot branding and handles native
  authentication-page logo/title/favicon and empty powered-footer fallback.
  Explicit custom footers remain intact; the site-wide footer setting is unchanged.
- No runtime JSON playback, Lottie dependency, CDN player, core source change,
  authentication setting change, route change or persisted Desktop relabeling.

## Verification results

Nine Python tests passed, covering idempotence, unrelated settings, asset URL
invalidation, saved-layout field preservation, native
navigation/provider data, existing custom footers, titles, the shared Login
JavaScript splash include and official theme variants. Five JavaScript tests
passed against the existing About, Desktop-avatar and native v16 sidebar/Help
contracts. Ruff, formatting, ESLint, Prettier and Git whitespace checks passed.

Live Chromium checks passed for:

- Login title **Login - ReyBill**, official black logo, native email/password
  validation, no visible Frappe/ERPNext branding, and 390 × 844 mobile Login.
- Forgot Password logo and native generic anti-enumeration response using an
  unregistered address, without sending email.
- Real native password login, native logout, one-time password reset and login
  with the new password, using a temporary Desk User with welcome mail disabled.
- Guest deep-link redirect to Login retaining `/desk/dashboard-view/CRM`, and
  successful authenticated CRM reload.
- Original PNG favicon hrefs and served PNG content on Login, Desktop, CRM,
  Home Workspace, Customer/Sales Invoice lists and an unsaved Customer form.
- Native tab titles: **Desktop**, **CRM Dashboard**, **Home**, **Customer** and
  **Sales Invoice**. Accounting is an installed Desktop folder: its dialog stays
  **Accounting**, and its tab stays **Desktop**. The unsaved Customer form keeps
  the native **New Customer - new-customer-…** title; no Customer was saved.
- About displays **ReyBill Core 0.0.4**, with no visible vendor branding.
- Supplied SVG animation visibly changes gradient pixels on desktop/mobile.
  Static fallback passes for failed animation requests, blocked component JS,
  JavaScript disabled and reduced motion. Reduced motion does not request the
  animated SVG. No animation JSON is requested in any case.
- A slow animation request neither blocks native startup nor reattaches the
  splash after Frappe removes it. Existing dark Desk uses the original white
  static logo. Automatic theme selection was additionally verified with the
  app-owned component rendered as a browser fixture: native picture/media
  selection works with JS disabled in light/dark modes, and changing motion
  preference stops the animation. No site/user theme preference was changed.
- Guest-only secondary audit finds no visible target vendor terms on Login,
  Reset Password, Complete Signup or the inspected Not Found page. Complete
  Signup's default footer now reads **Powered by ReyBill** with the centralized
  owned destination; its native form and signup configuration remain intact.
- No browser JavaScript errors in the successful site validation runs.

The native Forgot Password endpoint returned its generic 200 response in initial
runs. Repeated test submissions then reached its native one-hour rate limit.
Later reruns skipped that submission; the limiter was not disabled or cleared.
The development client may receive the native limit response until that window
expires. This is recorded separately from the successful reset UI/account test.

## Splash timing and screenshots

The test temporarily holds the native Desk bundle request to make the short-lived
splash observable. This delay exists only in the browser test and is not present
in application code. After releasing the request, Frappe's own
`Application.make_page_container()` removes `.splash`; measured values are in
the browser-results JSON and are below the four-second animation timeline.
The component introduces no minimum duration or timer.

| Evidence | Screenshot |
| --- | --- |
| Desktop Login | [login-desktop.png](login-desktop.png) |
| Mobile Login | [login-mobile.png](login-mobile.png) |
| Forgot Password | [forgot-password.png](forgot-password.png) |
| Reset Password | [reset-password.png](reset-password.png) |
| Native verification UI | [verification.png](verification.png) |
| Complete Signup / native footer | [complete-signup.png](complete-signup.png) |
| Desktop | [desktop.png](desktop.png) |
| CRM | [crm.png](crm.png) |
| Home Workspace | [workspace.png](workspace.png) |
| About version | [about-v0.0.4.png](about-v0.0.4.png) |
| Animated splash | [splash-animation.png](splash-animation.png) |
| Failed animation fallback | [splash-fallback.png](splash-fallback.png) |
| Reduced-motion fallback | [splash-reduced-motion.png](splash-reduced-motion.png) |
| Blocked component script | [splash-script-failure.png](splash-script-failure.png) |
| Mobile animated splash | [splash-mobile.png](splash-mobile.png) |
| Late animation fallback | [splash-late-animation.png](splash-late-animation.png) |

## Integrity, cleanup and limits

All 3,767 tracked Frappe files and 5,189 tracked ERPNext files match their fresh
preimplementation hashes. ERPNext's pre-existing `banking/yarn.lock` modification
is preserved. All six supplied SVG/PNG/JSON assets match their original hashes.
Desktop Icon, Workspace, Workspace Sidebar, Navbar Item and Has Role table
fingerprints remain unchanged. Desktop Layout also matched after temporary-user
cleanup, but the final comparison later found Administrator's saved layout
deleted. A native Deleted Document record records that deletion at 03:28:22 site
time on October 4. The current milestone contains no layout-reset/deletion calls;
the cause is awaiting user clarification. The current layout state has been left
untouched, rather than restoring a potentially intentional reset. All
unrelated Website/System settings and the **Frappe Framework** authenticator
issuer are unchanged, apart from standard modified metadata on the two updated
Single documents.

The temporary Desk User, generated Contact, sessions, test activity records and
protected credential/reset-token file were removed. Approved Administrator
sessions and their protected token files were removed. No credential, token or
site configuration is included in repository artifacts.

Signup, social providers and 2FA remain disabled on this site. Native OTP
presentation was rendered without enabling 2FA; real enrollment/provider login,
email delivery and signup completion were not exercised. Browser validation uses
Chromium with mobile viewport emulation; physical-device/Safari/Firefox playback
is not claimed. Other customer-visible vendor names and upstream destinations
remain classified in [WHITE_LABEL_AUDIT.md](../../WHITE_LABEL_AUDIT.md).

## Approved Desktop additions

The subsequent v0.0.4 Desktop requirements are documented and validated in
[DESKTOP_ADDITIONS.md](DESKTOP_ADDITIONS.md). They supersede the unchanged
Desktop-record and pending layout-state statements above for the expanded scope.
Native ordering/default visibility and the removed ReyBill artwork now use
supported record fields, while the navbar uses only its scoped theme adapter.

The final asset cache invalidation and native navbar sizing are recorded in
[BRANDING_FIXES.md](BRANDING_FIXES.md), including both themes and 320–1440 pixel
viewport results. All ReyBill sizing experiments and the Desktop stylesheet
hook were removed. Native Desk/Desktop CSS controls the logo dimensions, and
the original black/white source switching remains. The exact supplied PNG
filename and served-byte proof are documented. [Final release verification](RELEASE.md)
supersedes historical sizing and layout-state notes; it excludes every Reset test.
