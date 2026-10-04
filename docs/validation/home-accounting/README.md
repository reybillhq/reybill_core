# Home / Accounting correction validation

Site: `reybill.localhost`. Branch: `develop`. App version remains `1.0.0`.

## Correction

Home uses `reybill-icon-home.png`, copied byte-for-byte from the approved import (1254 × 1254 RGBA, 105,743 bytes). No recoloring, cropping, re-encoding or internal artwork change was made.

Accounting uses a new dedicated `reybill-icon-accounting.png`, a 512 × 512 RGBA PNG. It has one original ReyBill family frame (visible 440 × 440 with a 36px margin), containing four clean miniature glyphs isolated from the corresponding approved PNGs. No miniature tile backgrounds or borders are included. The offline builder reuses the Work asset's existing frame and approved glyph silhouettes/colors; all supplied sources remain unchanged. This is raster composition, not vector tracing or an SVG containing PNG data.

## Native identities and geometry

Read-only source inspection: Frappe `desk/page/desktop/desktop.js` `DesktopIcon.render_folder_thumbnail()` creates a `DesktopIconGrid` with all nine Accounting children. `DesktopIconGrid.prepare()` sorts by `idx`, then canonical label for ties. There is no source Accounting image and no explicit four-child slice. The outer folder clips the child grid.

At 1440px the measured native grid has six 18px columns, a 2.1px CSS gap, 16px image boxes and 7px parent padding. The 54px-wide parent exposes these fully visible positions:

| Position | Native identity / index | Approved glyph source |
| --- | --- | --- |
| Top-left | Invoicing / 0 | `reybill-icon-invoicing.png` |
| Top-right | Payments / 1 | `reybill-icon-payments.png` |
| Bottom-left | Budget / 6 | `reybill-icon-budget.png` |
| Bottom-right | Share Management / 7 | `reybill-icon-share-management.png` |

Measured image origins are (8, 8), (28.09375, 8), (8, 28.09375), (28.09375, 28.09375), relative to the parent. The effective image-box gap is 4.09375px; the underlying CSS gap is 2.1px. The offline composition keeps the 16/54 size and 20.09375/54 pitch proportions, centered within the new family frame.

The native mobile CSS differs: at 390px it forces two columns and shows Invoicing / Payments / Financial Reports / Accounts Setup instead. The dedicated asset deliberately preserves the observed **desktop** four at every width. [Native geometry](native-accounting-geometry.json) documents this rather than assuming the first four sorted children.

## Validation results

- Both corrected production URLs returned HTTP 200 and exact production bytes, using existing version/content-hash cache invalidation.
- Home has one approved PNG and no native `H` SVG or gray wrapper.
- Accounting has one dedicated composite PNG, no Accounts Setup main glyph, old SVG, blue wrapper or duplicate layer. The Accounts Setup child still uses its own approved PNG in the nine-item native folder.
- Light/dark and live theme switching passed at 1440, 768, 430 and 390px. All main image boxes remain the native 54px/50px squares with `contain`, no filtering and transparent native wrappers.
- Side-by-side first-row screenshots show unchanged family scale, margins, corner/border treatment and surrounding Desktop layout. The composite is not physically larger than other modules.
- Fresh navigation/reload and native desktop re-render retain mapping and ordering. Browser-only native translation/rendering shows Home as **Start** and Accounting as **Buchhaltung**, using the same stable IDs and assets without changing the User language setting.
- Accounting's native folder opens and Invoicing navigation still works. Home's native navigation and SPA return were separately checked; no callback or route was changed.
- Zero icon request failures, zero uncaught page errors, zero duplicate custom image layers and zero layout Save/Reset attempts.
- **10 Python tests and 6 JavaScript contracts passed**. The new composite test checks frame size/margin/color, clear 2×2 gutters, four separated glyph regions and absence of vendor blue. Ruff, ESLint, Prettier and whitespace checks passed.
- All six fresh before/after standard-table fingerprints match, including `Desktop Layout`. This correction began with zero saved layout records and ended with zero. No layout was saved, deleted, rebuilt, restored, migrated or reset.
- A real Reset Desktop Layout was deliberately not invoked because this correction explicitly prohibits layout resets. Native default startup and repeated-render contracts cover the corresponding icon-rendering state; Reset behavior/code is unchanged.
- Frappe/ERPNext source hashes and working-tree states match baseline. ERPNext's pre-existing `banking/yarn.lock` change remains untouched. All original 23 module imports, the newly supplied Home file and seven earlier official branding assets are unchanged.
- Existing icon JS/CSS adapters, ordering/setup code, navbar styling, app version, routes, module names and tags remain unchanged. Only the two central map entries and owned assets changed in production.

The earlier module-task Administrator layout history discrepancy has not been restored or modified. This correction uses a separate fresh baseline to prove it preserves current state.

## Durable evidence and local-only captures

- [asset-provenance.json](asset-provenance.json): Home source hash and derived Accounting composition identities/hash.
- [native-accounting-geometry.json](native-accounting-geometry.json): native folder geometry explaining the approved four glyphs.

Screenshots, raw browser/navigation/integrity outputs and the changed-file manifest remain local and untracked. They are excluded from the icon-system commit; the reusable read-only harness is `tests/validate_home_accounting.py`.

Only cache clearing was necessary; no bundle build, migration or site reset was run. The read-only browser harness blocks both native layout persistence endpoints. Temporary session credentials stayed in protected `/tmp` files and were removed. The existing native socket.io/undefined console issues documented in the previous icon validation are outside this correction.
