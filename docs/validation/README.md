# ReyBill Naming v0.0.2 validation

Validated on `reybill.localhost`, Frappe 16.36.1 and ERPNext 16.37.0, on 2026-10-04.

## Results

| Check | Result |
| --- | --- |
| Framework Desktop caption / folder title | `ReyBill Work` |
| ERPNext Settings Desktop caption / sidebar title | `ReyBill Settings` |
| Exact ERPNext display translation | `ReyBill`; no visible ERPNext Desktop Icon in the tested layout |
| Exact Frappe Framework display translation | `ReyBill Framework`; no separate Desktop Icon under that name |
| Profile menu | Edit Profile, Toggle Theme, About ReyBill, ReyBill Support, Reset Desktop Layout, Logout |
| Help menu | About ReyBill and ReyBill Support; Keyboard Shortcuts and System Health retained |
| ReyBill Support | A new tab received the configured URL from `branding.SUPPORT_URL` |
| Edit Profile | Native route `/desk/user/Administrator` opened |
| Toggle Theme | Native theme picker opened; no different theme was saved |
| About | Existing dialog opened, fetched versions and showed ReyBill Core 0.0.2; original callback retained |
| Framework navigation | Native app folder opened; Build child reached `/desk/doctype` |
| Settings navigation | Existing sidebar reached `/desk/global-defaults/Global%20Defaults` and rendered the native form |
| Reset Desktop Layout | Native method dispatched and page reloaded; deletion endpoint intercepted to preserve the saved layout |
| Logout | Native confirmation accepted; temporary session logged out and redirected to Login |
| Python regression tests | 3 passed: original-data preservation, idempotence, document/dict handling, final Desk context and website scoping |
| JavaScript native-source regression test | 1 passed: real installed v16 menu builder, native actions, extension items, repeated renders and script reloads |
| Ruff / ESLint / Prettier / JavaScript syntax / whitespace | Passed |
| Standard site records | Desktop Icon, Desktop Layout, Workspace, Workspace Sidebar, Navbar Item and Has Role fingerprints unchanged |
| Core source | All tracked-file fingerprints and working-tree status unchanged from the initial baseline |

ERPNext's pre-existing modified `banking/yarn.lock` remains as found. No commit was made.

The support tab's outbound request was intercepted; the test verifies destination and new-tab behavior without contacting the external site. The native reset deletion endpoint was intercepted because the user's saved layout must be preserved. This validates callback dispatch and native reload, rather than performing a destructive real layout reset.

No setup/migration is needed for these presentation-only hooks. Site cache was cleared. No asset build was needed: Frappe's Page loader appends `page_js` directly. Temporary browser/lint dependencies were placed under `/tmp`, without changing bench or core dependency manifests. Authenticated testing used explicitly approved temporary Administrator sessions; they were removed and their protected token file deleted after validation.

## Evidence

- [Desktop and profile menu](desktop-profile.png)
- [Existing About dialog](about-existing.png)
- [Existing theme picker](theme-existing.png)
- [Settings sidebar title](settings-navigation.png)
- [Help submenu](help-menu.png)
- [Unchanged Login screen](login-unchanged.png)
- [Exact browser observations](browser-results.json)

The settings and Help captures show only relevant controls, excluding unrelated company/account information. The full remaining-surface inventory is in [WHITE_LABEL_AUDIT.md](../WHITE_LABEL_AUDIT.md).

Known remaining rendered references include the untranslatable sidebar app subtitle `ERPNext`, the native About wordmark/heading/attribution and diagnostic package names, the theme option `Frappe Light`, and the native ERPNext login logo/favicon. Additional provider/product names and longer messages are documented in the audit. They were not included in the Desktop/profile-only implementation.

## Re-running focused checks

From the app root, use the bench virtual environment's Python:

```bash
../../env/bin/python -m unittest discover -s tests -p 'test_*.py'
node --test tests/desktop_naming.test.cjs
```

`tests/validate_browser.py` requires optional Playwright/Chromium tooling and a protected temporary session file. Obtain explicit approval before creating a privileged test session. The script accepts `--session-file`, `--url`, and `--output`; it never records the session credential in its output. Normal application use requires none of this test tooling.
