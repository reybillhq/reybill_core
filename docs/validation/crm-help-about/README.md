# CRM / Help / About validation

The full milestone was validated on `reybill.localhost` on 2026-10-04 with
Frappe 16.36.1, ERPNext 16.37.0 and ReyBill Core 0.0.2. The approved release
updates only the Core version to 0.0.3; the original browser results and
screenshots below retain their original version as historical evidence.

[Complete changed-file manifest](CHANGED_FILES.md) lists all implementation,
documentation, test, official asset and evidence files in the current milestone.

## v0.0.3 release verification

After the approved version-only change, site cache was cleared and the live
About dialog reported **ReyBill Core 0.0.3** through both the Desktop avatar
and CRM Help. The official black logo loaded unchanged; no Frappe/ERPNext
branding appeared in the customer dialog. Diagnostic boot data still reported
Frappe 16.36.1 and ERPNext 16.37.0 alongside Core 0.0.3.

Only the necessary version-related checks were rerun: 3 boot tests, 1 About
JavaScript test, formatting/lint for the changed version/test files, and focused
live About checks. The earlier full milestone validation below remains valid
for the unchanged CRM, Help, navigation and profile implementations.

- [Release About screenshot](about-v0.0.3.png)
- [Exact release observations](release-results.json)

The temporary Administrator session was removed and its protected token file
deleted. Standard-record fingerprints, original asset checksums and core
source/status were verified unchanged before the release commit.

## Live browser results

| Check | Observed result |
| --- | --- |
| CRM header | **CRM / ReyBill**; internal app ID remains `erpnext`, app title metadata remains `ERPNext` |
| CRM external promotion | No `Switch to Frappe CRM` item or external CRM promotional anchor exists in the rendered sidebar |
| CRM Desktop navigation | Native route `/desk/dashboard-view/CRM` opens |
| Help | **About ReyBill**, **Keyboard Shortcuts**, **System Health**, **ReyBill Support** |
| Contextual Help | Existing Global Settings documentation remains before the standard Help entries |
| About entry points | Desktop avatar, Framework/Build Help, Settings Help and CRM Help all open the ReyBill-owned dialog |
| Customer About text | About ReyBill; ReyBill; Business management software powered by ReyBill.; Version; ReyBill Core 0.0.2; Installed Applications; ReyBill; ReyBill Core; © ReyBill Ltd |
| About light logo | Original `/assets/reybill_core/images/branding/reybill-logo-black.svg`, successfully loaded; no CSS filter |
| About dark logo | Original white SVG variant, no CSS filter; verified without saving a theme preference |
| About vendor branding | No visible `Frappe`, `ERPNext`, `frappe:` or `erpnext:`; no upstream website/GitHub/forum/support links |
| About website | Single link uses `branding.SUPPORT_URL`; opens in a new tab |
| ReyBill Support | Desktop and CRM Help both open the configured `https://reybill.com/` destination in a new tab |
| Keyboard Shortcuts | Native dialog opens through CRM Help |
| System Health | Native System Health Report renders through CRM Help; saving remains disabled |
| Technical versions | Original `boot.versions` contains Frappe 16.36.1, ERPNext 16.37.0 and Core 0.0.2 |
| Native About implementation | Both `frappe.ui.toolbar.show_about` and `frappe.ui.misc.about` remain original |
| Workspace switching | Native CRM Workspaces menu switches to Selling |
| Desktop | ReyBill Work / ReyBill Settings captions and native folder/navigation behavior pass |
| Other profile actions | Edit Profile, Toggle Theme, Reset Desktop Layout dispatch and Logout pass |
| Logout | Native confirmation logs out the temporary validation session and redirects to Login |
| Browser errors | No uncaught page errors |

Support network requests were intercepted after opening the real popup, so the
test verifies new-tab behavior and destination without contacting the external
website. Reset's deletion endpoint was intercepted to preserve saved layouts;
its native callback and reload were exercised. Dark-logo checks changed only
the temporary page's theme attribute. No theme preference was saved.

Authentication used the explicitly approved temporary Administrator session,
with a 30-minute deadline. Logout removed the session; cleanup additionally
verified removal and deleted its protected temporary token file. No credentials
appear in the repository or evidence.

No separate `crm` application is installed on the development site. Its native
installed-app switch branch is covered by the regression test using the real
v16 sidebar source, rather than an end-to-end installed-CRM test.

## Preservation and focused checks

- All 3 Python tests and 4 JavaScript tests pass. They cover copied boot data,
  exact About action selection, preservation of metadata/version maps, native
  menu actions, unrelated Help items/banners, installed CRM switch links,
  repeated sidebar/Desktop renders, and official logo selection.
- Ruff check/format, ESLint, Prettier, JavaScript syntax and Git whitespace
  checks pass.
- Fresh fingerprints for Desktop Icon, Desktop Layout, Workspace, Workspace
  Sidebar, Navbar Item and Has Role records remain unchanged after validation.
- All 3,767 tracked Frappe files and 5,189 tracked ERPNext files have identical
  checksums and Git status before/after. ERPNext's pre-existing
  `banking/yarn.lock` change remains untouched.
- All six supplied assets retain their original SHA-256 checksums. Only the
  static branding directory casing changed. All lowercase logo/icon URLs and
  unchanged animation URLs serve the original bytes on the development site.
- Site cache was cleared. No migration, asset bundle rebuild, splash
  implementation, player dependency, or core dependency change was needed.

## Evidence

The captures show branding controls and dialogs, excluding unrelated company
settings and System Health data. The About application labels use the native
uppercase styling for their section heading.

- [CRM sidebar](crm-sidebar.png)
- [CRM Help](crm-help.png)
- [ReyBill About](about-reybill.png)
- [Dark About](about-dark.png)
- [About from CRM](about-crm-help.png)
- [About from Framework/Build](about-framework-help.png)
- [About from Settings](about-settings-help.png)
- [Settings Help](help-menu.png)
- [Keyboard Shortcuts](keyboard-shortcuts.png)
- [System Health heading](system-health-title.png)
- [Selling navigation](selling-navigation.png)
- [Desktop profile menu](desktop-profile.png)
- [Settings sidebar heading](settings-navigation.png)
- [Native theme picker](theme-existing.png)
- [Unchanged Login](login-unchanged.png)
- [Exact browser observations](browser-results.json)

## Remaining references

No target vendor names remain in the ReyBill-owned About text or the two
requested Help entries. Outside this scope, the native **Frappe Light** theme
option, ERPNext login logo/favicon and Framework Desktop icon remain. Source
and site audit candidates include Support's Helpdesk promotion, CRM/Support
workspace content notices, external contextual documentation destinations,
Frappe Mail and CRM integration labels, setup/onboarding messages, email and
website footer defaults, and other longer vendor-specific messages. These
have not been globally replaced. See [WHITE_LABEL_AUDIT.md](../../WHITE_LABEL_AUDIT.md).

## Re-run

From the app root:

```bash
../../env/bin/python -m unittest discover -s tests -p 'test_*.py'
node --test tests/desktop_naming.test.cjs tests/desk_branding.test.cjs tests/about.test.cjs
```

`tests/validate_browser.py` requires optional Playwright/Chromium tooling and
an authorized protected session file. Its default output directory is this
milestone's folder, so it does not overwrite the frozen v0.0.2 evidence.
