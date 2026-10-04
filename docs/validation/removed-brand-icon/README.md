# Removed ReyBill application tile correction

Validated on `reybill.localhost`, 2026-10-04. This correction is part of the approved module icon milestone; version and historical release tags are unchanged.

## Exact correction

The native Desktop Icon identity is `ERPNext`; its translated caption is `ReyBill`. Before this correction it had no entry in `MODULE_ICONS`, so native rendering fell back to the existing persistent `logo_url`:

`/assets/reybill_core/images/branding/Reybill_desk_icon.png?v=1.0.0&h=c2b0e400d772`

One entry in `reybill_core/branding.py` now maps `ERPNext` through the existing `branding_asset_url()` constructor to:

`/assets/reybill_core/images/branding/module-icons/reybill-icon-reybill.png?v=1.0.0&h=955c8d8e6779`

The existing boot metadata and module adapter consume this entry for the native Removed Icons pane. No JS/CSS adapter, order, route, record, migration or setup logic was changed. Native `data-logo` metadata and the original persistent-logo constant remain unchanged; the visible `<img src>` uses the new mapped PNG. The old file remains intact.

The production PNG matches the approved import byte-for-byte: 63,375 bytes, 1254 × 1254 RGBA, SHA-256 `955c8d8e677991fd1866022c4b0d3a5509657f98d30573b5cdc7dc92429feba4`.

## Browser and saved-layout safety

The focused `tests/validate_removed_brand_icon.py` harness blocks the native `save_layout` and `delete_layout` endpoints. Edit mode uses native setup, followed only by Discard. Add, Save and Reset are never clicked; the tile is never restored, including in browser memory. The native Add callback functions are compared against the pre-change browser baseline and are identical; their action was deliberately not executed.

- Light and dark themes, reload and SPA navigation to Invoicing/back: all six states passed.
- Tile remains under Removed Icons with `hidden=1`, original pane position and native Add button mode/callbacks.
- Active order remains the same 15 canonical Desktop Icon identities; `ERPNext` is absent from the active grid/order.
- Framework/Work, Home and Accounting still render their existing work/home/accounting PNGs.
- Exactly one image and no SVG layer in the tile container; transparent wrapper, no shadow, zero padding and `object-fit: contain`. No native blue background remains.
- The new version/hash URL returns HTTP 200 and exactly the production/source PNG bytes.
- Zero layout save/delete requests, zero Reset calls and zero JavaScript page errors.
- No new console error categories compared with the pre-change run. Existing Socket.IO HTTP 404/polling errors and `/undefined` 404 remain. Polling timestamps differ and are excluded from category comparison; baseline/after totals were 24/26.
- All six table fingerprints match before/after: Desktop Icon, Desktop Layout, Workspace, Workspace Sidebar, Navbar Item and Has Role. No Administrator or other saved layout was written, deleted or reset. Desktop Layout count remains zero.
- All 32 existing image/animation files, including all 25 module PNGs, are unchanged.
- All 3,767 tracked Frappe and 5,189 tracked ERPNext file hashes and working-tree statuses match the captured baseline. ERPNext's pre-existing `banking/yarn.lock` modification remains untouched.
- Ten Python tests and six JavaScript contracts passed. Ruff lint/format and `git diff --check` passed.

Only site cache clearing was needed. These validation runs performed no build, migration, setup, layout reset, staging, commit or push. The authorized temporary Administrator session was removed after testing; no session credentials are stored in these artifacts.

## Durable evidence and local-only captures

- [Pre-change comparison](baseline-comparison.json): exact old/new asset URL, callback/state comparison and console categories.
- [Asset, standard-record and upstream integrity](integrity.json): compact checksum and read-only safety results.

Light/dark screenshots and raw browser states remain local and untracked; they are excluded from the icon-system commit. The reusable read-only harness is `tests/validate_removed_brand_icon.py`.

Existing files touched by this delta: `reybill_core/branding.py`, `docs/BRANDING_ASSETS.md`, `docs/REYBILL_MODULE_ICONS.md`, and the current `tests/validate_module_icons.py` image expectation. New files: the focused read-only harness and this validation directory. Earlier module/Home/Accounting changes remain preserved.
