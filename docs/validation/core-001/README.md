# CORE-001 — redundant ReyBill Core launcher

Development fix; stable fresh-site acceptance is pending. App version remains
1.3.0. The next available proposed patch version is 1.3.1. No release tag is
created by this implementation milestone.

## Confirmed identity and cause

The user supplied the fresh site's live boot data on Frappe 16.36.1:

| Field | Value |
| --- | --- |
| Desktop Icon name | `ReyBill Core` |
| Application | `reybill_core` |
| Icon type | `App` |
| Link type / link | `External` / `/app` |
| Standard / hidden | `0` / `0` |
| Logo | `/assets/reybill_core/images/branding/Reybill_desk_icon.png` |

The corresponding app registry still names `reybill_core`, with title
`ReyBill ERP`, module `ReyBill Core`, and no workspaces. This app registry is
not the launcher and is preserved.

The direct bug is a persisted redundant App Desktop Icon being admitted to
customer Desktop data, including independently saved layout copies. Its
External link is used by native `get_route()`; `/app` is the legacy Desk entry
and routes back to Desk. The fix does not change this route or the record.

Native Frappe's `after_app_install` hook calls
`frappe.utils.install.auto_generate_icons_and_sidebar()`, which calls
`create_desktop_icons_from_installed_apps()`. That factory reads each installed
app's `add_to_apps_screen` hook, sets `app` to the package identifier, names the
record from `app_title`, copies the registered route/logo, and saves it.
Existence checks prevent repeated creation; normal boot subsequently reads the
persisted records. The v16 generation migration patch can also invoke the
factory. The isolated native-source test verifies both the registration recipe
and the absence of a new Core launcher when the current hooks are used.

However, the current ReyBill repository and its tracked hook history have no
active `add_to_apps_screen` registration. The fresh site's `ReyBill ERP` app
title also differs from current `hooks.py` (`ReyBill Core`). The supplied boot
row proves the target identity, not its original creation provenance. Earlier
deployment metadata, a fixture or manual creation cannot be distinguished
without fresh-site installation/history evidence. No unsupported claim that
the current package automatically creates it is made. Changing current
registration would not remove this existing row, and there is no applicable
native read-side exclusion setting in the inspected v16 source.

The development site's read-only baseline contains 36 Desktop Icons, no
`reybill_core` icon, and zero saved Desktop Layouts. Its independent
`Framework` record is ReyBill Work; its hidden `ERPNext` record is the separate
ReyBill item. Neither is a CORE-001 target.

## Implementation

`EXCLUDED_DESKTOP_LAUNCHERS` in `branding.py` contains exactly the verified
`("reybill_core", "ReyBill Core")` pair. Both fields must match. Captions,
translations, icon positions, app title, routes and image URLs are not removal
keys. Other Core-owned records remain eligible.

The existing `extend_bootinfo` integration uses a pure filter from `desktop.py`
to remove this pair from the presentation list. The original cached list and
rows remain intact. The existing final Desk-context hook reapplies it to shared
session boot data. `app_data`, technical versions and dynamic About installed
apps are untouched.

The existing `page_js["desktop"]` adapter installs an instance-level wrapper
after native `on_page_load` and before the first `on_page_show`. It filters only
the runtime list consumed by native `DesktopPage.prepare()`. This is necessary
because native `sync_layout()` can restore a saved layout independently of
boot data on every render. Normal and edit-mode preparation are both covered.
Native preparation builds the active grid and the Removed Icons list from this
filtered input, so the launcher cannot become a selectable removed item.

The adapter does not change `desktop.data`, saved JSON, browser storage or
database records. It preserves original receiver, arguments, return values and
all unrelated row fields, including indices and hidden/folder state. Installation
is guarded against repeated script loads. There is no DOM removal, CSS hiding,
observer, polling, callback replacement or reordering for this fix. Existing
avatar branding remains unchanged.

No migration, setup hook, icon recreation, layout reset or database deletion is
required. Existing install/migrate branding/order code is unchanged and was not
invoked during this validation. This fix itself performs no persistence writes.

## Automated validation

- 23 isolated Python tests pass, including six new CORE-001 contracts.
- 11 JavaScript contracts pass, including five new CORE-001 contracts that
  execute the installed native Desktop lifecycle, preparation, saved-layout
  synchronization and Removed Icons code against isolated data.
- Coverage includes the exact fresh-site row, default ordering, Framework/Work
  and Home, other canonical modules, customized order/indices, hidden rows,
  same captions with different identities, other Core-owned shortcuts, native
  Accounting folder grouping, edit mode and repeated renders/script loads.
- App registry and real dynamic About helper contracts retain ReyBill Core as
  installed; technical versions remain unchanged.
- The native install factory is executed only against mocked hooks/documents.
  These are installation contracts, not a real fresh-site installation.
- Ruff lint/format, ESLint, Prettier, Git whitespace and pre-commit checks are
  run for the final implementation.
- Existing Frappe Cloud compatibility remains
  `frappe = ">=16.0.0-dev,<17.0.0"`; the packaging regression test passes.

No authentication session is created or injected. No actual fresh install,
live UI screenshots or desktop/mobile visual acceptance is claimed. No
authorized reusable authenticated browser or designated disposable site is
available in this environment. Live site inspection uses read-only
transactions; saved layout and icon snapshots are compared separately from
these isolated regression tests.

## Developer acceptance before stable release

1. Deploy the CORE-001 fix from **origin/develop**, not the still unchanged
   `version-16` branch. Record the installed Core commit and Frappe/ERPNext
   versions. Normal deployment must refresh running Python modules and Desk
   caches through the supported deployment lifecycle. No new migration is
   needed for the exclusion; do not run install/migrate/reset on an existing
   customized site just to validate it.
2. On an explicitly disposable fresh ERPNext v16 site with ReyBill Core
   installed, sign in normally and open Desk. Confirm no `ReyBill Core` tile
   in the normal grid, active customization or Removed Icons.
3. Confirm canonical default order: ReyBill Work, Home, Organization,
   Accounting, Assets, Buying, CRM, Manufacturing, Projects, Quality, Selling,
   Stock, Support, Subcontracting, ReyBill Settings; preserve native Workspace
   creation/navigation where it is available. No ordering change is part of
   CORE-001.
4. Confirm the separate removed ReyBill/ERPNext tile stays removed with its
   approved artwork. Confirm all other module artwork and navigation remain
   unchanged.
5. Reload and navigate away/back several times; inspect both active and removed
   choices again. Check 1440px and 390px (and dark theme if used), without
   changing geometry or saving theme/layout preferences for this test.
6. Confirm About ReyBill still lists installed ReyBill Core with its actual
   version; other installed ReyBill apps remain listed.
7. On an existing customized site containing the launcher, compare saved
   Desktop Layout JSON/checksums before and after read-only rendering. Confirm
   every other index, removal state and folder relationship remains intact.
   Do not click Save or Reset. The stored redundant row may remain; only its
   customer-facing presentation is excluded.
8. Report fresh-site acceptance and approve the stable release. Until then,
   leave both branches' versions at 1.3.0 and do not create `v1.3.1`.

For a read-only identity check after deployment:

```js
console.log(JSON.stringify({
  redundantBootIcons: frappe.boot.desktop_icons.filter(
    i => i.app === "reybill_core" && i.name === "ReyBill Core"
  ),
  redundantRuntimeIcons: (frappe.desktop_icons || []).filter(
    i => i.app === "reybill_core" && i.name === "ReyBill Core"
  ),
  coreRegistry: frappe.boot.app_data.filter(a => a.app_name === "reybill_core"),
  about: frappe.boot.reybill_branding.about.applications
}, null, 2));
```

Both redundant lists should be empty while `coreRegistry` and `about` still
contain the installed Core application. After opening native Edit Layout,
inspect `frappe.pages.desktop.desktop_page.hidden_icons` with the same exact
pair; it must also be absent. Discard; never Save or Reset for this validation.

The stable release must cherry-pick only this approved fix and packaging commit
`1841082cf7e6fc265ba68149534281d5e7b96955`, then follow the approved branch-version
policy, final tests and annotated tag workflow. Do not merge all development
history or rewrite historical tags.

## Source references

- [Frappe supported boot hook](https://docs.frappe.io/framework/user/en/python-api/hooks#extend-bootinfo)
- [Native v16.36.1 Desktop Icon generation](https://github.com/frappe/frappe/blob/v16.36.1/frappe/desk/doctype/desktop_icon/desktop_icon.py)
- [Native v16.36.1 Desktop lifecycle and Removed Icons](https://github.com/frappe/frappe/blob/v16.36.1/frappe/desk/page/desktop/desktop.js)
- [Native page_js loading](https://github.com/frappe/frappe/blob/v16.36.1/frappe/core/doctype/page/page.py)
