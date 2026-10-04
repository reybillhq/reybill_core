# ReyBill module icons

Implemented on `develop` after the frozen v1.0.0 baseline. App version and historical release tags remain unchanged; the icon milestone is a new commit on `develop`.

## Source and immutable inventory

Read-only approved source: `/home/frappe/reybill-icon-import/`.
Production copies: `reybill_core/public/images/branding/module-icons/`.
The original 23 imports and the newly supplied Home PNG keep their exact incoming filenames and SHA-256 hashes. No artwork was redrawn, cropped, recolored, optimized, converted or re-encoded. PNG canvases, transparent margins and glyph scales are preserved.

Every supplied file is `.png`, **RGBA**, with an alpha channel containing transparent pixels (alpha range 0–255). Financial Reports is 1024 × 1024; the other 23 supplied PNGs are 1254 × 1254. The additionally composed Accounting PNG is 512 × 512. The initial 23-file inventory, including byte sizes and full hashes, is [import-inventory.json](validation/module-icons/import-inventory.json). Home and the derived Accounting composite are documented in [asset-provenance.json](validation/home-accounting/asset-provenance.json).

| Production/import filename | Dimensions | Bytes | Stable Desktop Icon name → intended surface |
| --- | --- | ---: | --- |
| `reybill-icon-accounts-setup.png` | 1254 × 1254 | 793,442 | Accounts Setup |
| `reybill-icon-home.png` | 1254 × 1254 | 105,743 | Home |
| `reybill-icon-accounting.png` | 512 × 512 | 42,500 | Accounting (dedicated composite) |
| `reybill-icon-assets.png` | 1254 × 1254 | 61,703 | Assets |
| `reybill-icon-banking.png` | 1254 × 1254 | 56,925 | Banking |
| `reybill-icon-budget.png` | 1254 × 1254 | 646,702 | Budget |
| `reybill-icon-buying.png` | 1254 × 1254 | 72,720 | Buying |
| `reybill-icon-crm.png` | 1254 × 1254 | 72,414 | CRM |
| `reybill-icon-financial-reports.png` | 1024 × 1024 | 51,402 | Financial Reports |
| `reybill-icon-invoicing.png` | 1254 × 1254 | 68,568 | Invoicing |
| `reybill-icon-manufacturing.png` | 1254 × 1254 | 64,887 | Manufacturing |
| `reybill-icon-organization.png` | 1254 × 1254 | 63,572 | Organization |
| `reybill-icon-payments.png` | 1254 × 1254 | 65,178 | Payments |
| `reybill-icon-projects.png` | 1254 × 1254 | 64,295 | Projects |
| `reybill-icon-quality.png` | 1254 × 1254 | 72,482 | Quality |
| `reybill-icon-reybill.png` | 1254 × 1254 | 63,375 | ERPNext (removed ReyBill application tile) |
| `reybill-icon-selling.png` | 1254 × 1254 | 64,323 | Selling |
| `reybill-icon-settings.png` | 1254 × 1254 | 79,551 | ERPNext Settings (ReyBill Settings) |
| `reybill-icon-share-management.png` | 1254 × 1254 | 62,848 | Share Management |
| `reybill-icon-stock.png` | 1254 × 1254 | 62,294 | Stock |
| `reybill-icon-subcontracting.png` | 1254 × 1254 | 73,216 | Subcontracting |
| `reybill-icon-subscription.png` | 1254 × 1254 | 60,811 | Subscription |
| `reybill-icon-support.png` | 1254 × 1254 | 69,497 | Support |
| `reybill-icon-taxes.png` | 1254 × 1254 | 71,950 | Taxes |
| `reybill-icon-work.png` | 1254 × 1254 | 73,669 | Framework (ReyBill Work) |

Home now uses the newly supplied `reybill-icon-home.png`, copied without any byte changes. Workspace/My Workspaces retains its native artwork/action. The removed Desktop Icon internally named `ERPNext` remains removed and now displays `reybill-icon-reybill.png` through the same presentation-only map. Its original database/layout `logo_url` and technical identity remain untouched; the old `images/branding/Reybill_desk_icon.png` is retained.

## Existing implementation audit and mechanism

The existing `branding.py` owns branding URLs, label maps, canonical order and the removed ReyBill icon. `boot.py` supplies presentation metadata; existing JS adapts menu/sidebar labels and the theme-aware navbar logo. No previous per-module artwork map existed. `desktop.py` and `setup.py` contain the existing persisted order/setup logic; neither file is changed or invoked by this task.

New `MODULE_ICONS` in `reybill_core/branding.py` is the **single** map, keyed by original Desktop Icon document names. The map is copied into `frappe.boot.reybill_branding.module_icons`; native boot icon records, routes, app IDs and saved layouts are not changed. The native lookup receives untranslated canonical labels and resolves them to the record's stable `name`, which selects the map; translated visible text is not a selector.

Hooks load the app-owned `public/js/module_icons.js` and `public/css/module_icons.css` through the existing `branding_asset_url()` constructor. All production URLs begin `/assets/reybill_core/images/branding/module-icons/` and carry both `v=<app version>` and `h=<12-character SHA-256>`. Changed asset bytes invalidate their URL even before a version bump. No new caching system or global cache policy is introduced.

The installed v16 source has no dedicated per-module icon override hook. The scoped client adapter extends its native icon-rendering functions:

1. `frappe.utils.get_desktop_icon()` returns the approved URL for a confidently resolved mapped record; unmatched records delegate to the original lookup with its arguments, receiver and result preserved. Native Desktop images, sidebar headers and the native Workspace switcher consume this same lookup.
2. The native `desktop_screen` event supplies real Desktop Icon objects. A guarded post-render wrapper calls `DesktopIcon.render_folder_thumbnail()` normally, then changes only a mapped object's direct `.icon-container` artwork. This keeps Accounting as a functional native Folder while presenting its dedicated composite asset. The same native class builds folder modal, new and edit-mode tiles.
3. Native `Workspace.show_page()` is followed only for a mapped actual Workspace name with an existing `.workspace-icon` slot. No new icon slots or cards are created. Neither tested Accounting Workspace renders such a slot in this installed build; their actual sidebar headers are mapped instead.

Each adapter installs once and preserves original navigation handlers, return values, technical identifiers, roles, permissions and order. There are no observers, polling loops, global string replacement or layout persistence writes. These narrow v16 function adapters should be revalidated when upstream rendering changes; the contract test covers fallback, repeated installation, folder behavior and stable names with translated labels.

The CSS applies only to mapped ReyBill module image containers. Their native background, shadow, padding and clipping treatment are neutralized; the PNG supplies its own approved tile. Native rendering boxes and surrounding layout remain unchanged. Images use `object-fit: contain` and no filter in both themes. Sidebar/menu image rules select only the owned module-icon asset prefix; toolbar, form, report, notification and unmapped system icons are untouched.

## Accounting surfaces

All nine children under native Folder `Accounting` are `Desktop Icon` links targeting their same-named `Workspace Sidebar`, owned technically by `erpnext`:

| Internal name | Approved PNG suffix | Applied surface |
| --- | --- | --- |
| Accounts Setup | `accounts-setup` | Accounting modal tile; native sidebar header/switcher entry |
| Banking | `banking` | Accounting modal tile; native sidebar header/switcher entry |
| Budget | `budget` | Accounting modal tile; native sidebar header/switcher entry |
| Financial Reports | `financial-reports` | Accounting modal tile; native sidebar header/switcher entry |
| Invoicing | `invoicing` | Accounting modal tile; native sidebar header/switcher entry |
| Payments | `payments` | Accounting modal tile; native sidebar header/switcher entry |
| Share Management | `share-management` | Accounting modal tile; native sidebar header/switcher entry |
| Subscription | `subscription` | Accounting modal tile; native sidebar header/switcher entry |
| Taxes | `taxes` | Accounting modal tile; native sidebar header/switcher entry |

Only Financial Reports and Invoicing also have same-named actual `Workspace` documents. Other children have valid sidebars without a same-named Workspace document. Text-only Accounting/Invoicing link-card groups have no original icon slot and remain text-only. Matching words in field labels, reports, DocTypes or business data are never used as icon targets. The native record evidence is [native-surfaces.json](validation/module-icons/native-surfaces.json).

## Adding another approved icon

Copy the approved source bytes into the production folder using `reybill-icon-<module>.png`. Identify the existing stable Desktop Icon name (and actual Workspace if applicable), then add only that entry to `MODULE_ICONS` using `branding_asset_url()`. Do not rename a module, create a Workspace, edit upstream source or redesign the artwork to manufacture a target. Run the contract tests and browser checks for the real surface. No migration is required for this presentation-only implementation.

## Validation

See [validation notes](validation/module-icons/README.md). Tests include default and customized Desktop rendering, both themes, five viewport widths, all Accounting modal icons, native child navigation, route return, reload and native Reset **only on a disposable copied layout**. Existing user layouts are never reset or saved by this task.

Frappe/ERPNext source and existing official branding assets match their captured baselines. Standard-record and saved-layout comparisons are reported separately in the validation notes; an earlier Administrator save/deletion discrepancy is recorded without reconstructing or overwriting current user state. The later read-only correction fingerprints all match. `desktop.py`, `setup.py`, the navbar CSS and `__init__.py` remain unchanged. Cache was cleared; no asset bundling or migration was needed for these directly served CSS/JS/PNG files.

## Targeted Home / Accounting correction

`Home` maps to `reybill-icon-home.png`. `Accounting` now maps to `reybill-icon-accounting.png`, never to Accounts Setup. The Accounts Setup child mapping is unchanged. No JS/CSS adapter or layout/order behavior was refactored.

The native folder renderer creates all nine children, sorted by `idx` (canonical label breaks ties). At 1440px the inherited six-column grid is clipped by its folder: fully visible positions are Invoicing (index 0) / Payments (1), then Budget (6) / Share Management (7). At 390px native CSS uses two columns and instead exposes indices 0–3. The dedicated asset intentionally preserves the **observed desktop** four consistently at every width. This responsive discrepancy and exact native bounds are recorded in [native-accounting-geometry.json](validation/home-accounting/native-accounting-geometry.json).

The offline script `scripts/build_accounting_icon.py` composes a genuine PNG from the four supplied raster glyphs; it does not trace them or wrap raster data in SVG. It isolates existing foreground coverage, retains opaque source colors/geometry, and reuses the official Work tile frame/alpha without modifying any source file. There is one parent frame, with no four nested module-tile backgrounds. At a 512px canvas the visible outer tile is 440px with a 36px margin. Native 16/54 image-box proportions and measured 20.09375/54 cell pitch are preserved, centered within that family tile. Pillow is an offline composition tool only; no frontend/runtime dependency was added.

[Correction validation](validation/home-accounting/README.md) is strictly read-only: all native layout Save/Reset endpoints were blocked in the test browser. No Reset, migration, layout reconstruction or saved-layout write was performed. Fresh before/after fingerprints are compared independently of the earlier module-task layout discrepancy.

## Removed ReyBill application tile correction

`MODULE_ICONS["ERPNext"]` selects the existing approved `reybill-icon-reybill.png`, using the existing release/content-hash URL constructor. The native edit pane uses the same Desktop Icon class and adapter as the active grid; no extra adapter or JS/CSS change is needed. ReyBill Work remains mapped to `Framework` / `reybill-icon-work.png`. Home, Accounting and canonical ordering are unchanged. The legacy persistent-logo constant and setup/migration logic are deliberately unchanged and are not invoked by this correction.

See [read-only validation](validation/removed-brand-icon/README.md). The Add callback is inspected and compared with the pre-change browser baseline; Add, Save and Reset are never clicked. All layout Save/Delete endpoints are blocked, and all six standard-record table fingerprints are compared before and after.
