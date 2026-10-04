# v0.0.4 Desktop additions

The only new client presentation adapter targets `#brand-logo`, using the
central official black/white SVG paths. Native `set_theme` keeps its arguments,
return value and effects; its resolved theme determines the logo. The native
Desktop event refreshes the image on each render. No dimensions, layout,
clicks, other images or icon artwork are changed. No observer is added.

## Ordering and state

`reybill_core/desktop.py` uses native Desktop Icon `idx` fields and saved
Desktop Layout JSON indices. It never changes names, captions, routes, roles,
links or folder/workspace relationships. Home, CRM and Support are visible in
the explicitly approved default, matching their original saved visibility.
Saved layouts preserve removal flags. Only the internally named ERPNext icon's
`logo_url` is replaced with the exact supplied `Reybill_desk_icon.png` path.
Its default removed state remains `hidden = 1`.

Setup runs after installation and migration, after upstream imports, and is
idempotent. Native Reset discards a saved layout and reads these default
records. Native editing, removal, dragging and save behavior remain available.
Supported `Document.db_set` avoids standard-record export into core app folders
in developer mode; caches are cleared explicitly when fields change.

The observed native grid is:

| Row | Icons |
| --- | --- |
| 1 | ReyBill Work, Home, Organization, Accounting, Assets, Buying |
| 2 | CRM, Manufacturing, Projects, Quality, Selling, Stock |
| 3 | Support, Subcontracting, ReyBill Settings |

**Workspace is the native Add New Workspace action, appended last in edit
mode**, yielding the requested sixteenth tile there. This installed v16 site
has no persistent Desktop Icon named Workspace. No new workspace or destination
was invented. The separate conditional My Workspaces icon is unchanged.

During testing, Administrator's layout was edited to show ERPNext/ReyBill and
then reset/deleted. No ReyBill setup or browser harness changed that hidden
flag or deleted the layout; a proposed restoration found that the record had
already been deleted and made no write. Final checks use native defaults, with
ReyBill removed. This supersedes the earlier pending layout-state note in the
original milestone report.

## Validation

- Migration completed successfully on `reybill.localhost`; indices and artwork
  survived native standard import and after-migrate setup.
- Light and dark were chosen through native Toggle Theme. The correct SVG
  changed at runtime, and persisted on reload in each theme.
- Both themes retained the same native logo bounds: 42.65625 × 32 pixels.
  The supplied SVG canvas whitespace is unchanged.
- The native edit-mode Removed Icons pane displays ReyBill with the supplied
  PNG; it stays removed when edit mode is discarded.
- Native default render path, used after Reset, has the canonical ordering.
  Validation did not delete any saved user layout.
- All 35 native Desktop Icon records retain their original navigation,
  relationships, artwork and state except the approved indices, three default
  visibility flags and ERPNext logo URL.
- All 3,767 tracked Frappe and 5,189 tracked ERPNext file bytes remain unchanged.
  ERPNext's pre-existing `banking/yarn.lock` modification is preserved.
- All six original official assets and the newly supplied Desktop PNG retain
  their original bytes. No animation dependency was installed.
- Seven Python tests, five JavaScript tests, Ruff and scoped ESLint checks pass.

Evidence:

- [Light Desktop](desktop-light.png)
- [Dark Desktop](desktop-dark.png)
- [Removed icon and native Workspace tile](desktop-removed-icon.png)
- [Desktop browser results](desktop-additions-results.json)
- [Record/core/asset integrity results](desktop-integrity-results.json)
- [Native authentication and order results](desktop-auth-results.json)

A native invalid-password check initially exposed a closed development-server
output pipe: `frappe.errprint` raised `BrokenPipeError` during exception handling.
Only the development web process was restarted with a valid protected log stream.
No framework or application source/configuration was changed for that repair.
The native invalid-credentials response and visible error banner then worked.

Actual temporary-user password login, Enter-to-submit, reload and logout/login
preserved the permission-filtered order. A logged-out `/desk/crm` request returned
to that route after authentication. Native invalid-password HTTP 401 and the
visible error banner, Forgot Password navigation and zero browser page errors
were verified. The temporary test user/contact, sessions and protected credential
files were removed. The approved Administrator test session was removed.
No authentication settings, roles or framework version data were altered.
